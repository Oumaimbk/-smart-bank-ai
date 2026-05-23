from pathlib import Path
from typing import Optional

import pandas as pd
from django.conf import settings
from django.db.models import Avg, Count, Sum
from django.db.models.functions import TruncMonth
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.transactions.models import Transaction

from .models import MLModelMetrics


class DashboardKPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        qs = Transaction.objects.filter(user=request.user)
        total_credit = qs.filter(direction='Credit').aggregate(v=Sum('amount'))['v'] or 0
        total_debit = qs.filter(direction='Debit').aggregate(v=Sum('amount'))['v'] or 0
        return Response({
            'total_credit': float(total_credit),
            'total_debit': float(total_debit),
            'net_balance': float(total_credit - total_debit),
            'transaction_count': qs.count(),
            'debit_count': qs.filter(direction='Debit').count(),
            'credit_count': qs.filter(direction='Credit').count(),
        })


class SpendingByCategoryView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        data = (
            Transaction.objects
            .filter(user=request.user, direction='Debit')
            .values('category')
            .annotate(total=Sum('amount'), count=Count('id'), average=Avg('amount'))
            .order_by('-total')
        )
        return Response(list(data))


class MonthlyEvolutionView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        data = (
            Transaction.objects
            .filter(user=request.user)
            .annotate(month=TruncMonth('transaction_date'))
            .values('month', 'direction')
            .annotate(total=Sum('amount'))
            .order_by('month', 'direction')
        )
        return Response(list(data))


class TopMerchantsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        data = (
            Transaction.objects
            .filter(user=request.user, direction='Debit')
            .exclude(merchant_name='')
            .values('merchant_name')
            .annotate(total=Sum('amount'), count=Count('id'))
            .order_by('-total')[:10]
        )
        return Response(list(data))


class MLMetricsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        _ensure_rf_metrics()
        _ensure_classifier_metrics()

        models_data = []
        for record in MLModelMetrics.objects.all().order_by('model_name'):
            models_data.append({
                'model_name': record.model_name,
                'display_name': _DISPLAY_NAMES.get(record.model_name, record.model_name),
                'task': _TASKS.get(record.model_name, ''),
                'metrics': record.metrics,
                'sample_count': record.sample_count,
                'computed_at': record.computed_at,
            })

        return Response({'models': models_data})


class FeatureImportanceView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        _ensure_rf_metrics()
        try:
            record = MLModelMetrics.objects.get(model_name='random_forest')
        except MLModelMetrics.DoesNotExist:
            return Response({'features': [], 'model': 'Random Forest Regressor', 'computed_at': None})

        features = [
            {**f, 'rank': i + 1, 'importance_pct': round(f['importance'] * 100, 1)}
            for i, f in enumerate(record.feature_importance)
        ]
        return Response({
            'features': features,
            'model': 'Random Forest Regressor',
            'computed_at': record.computed_at,
        })


_DISPLAY_NAMES = {
    'random_forest': 'Random Forest Regressor',
    'logistic_regression': 'TF-IDF + Régression Logistique',
}
_TASKS = {
    'random_forest': 'Prévision des dépenses mensuelles',
    'logistic_regression': 'Catégorisation des transactions',
}


def _ensure_rf_metrics():
    """
    Lazily extract feature importance and basic metrics from an existing
    Random Forest pkl if no DB record exists yet (e.g. model trained before
    the metrics-saving code was added).
    """
    if MLModelMetrics.objects.filter(model_name='random_forest').exists():
        return
    try:
        from pipeline.prediction.trainer import (
            ENCODER_PATH, FEATURE_LABELS, MODEL_PATH,
        )
        import joblib
        import numpy as np
        import pandas as pd
        from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
        from sklearn.model_selection import train_test_split

        if not MODEL_PATH.exists():
            return

        model = joblib.load(MODEL_PATH)

        feature_importance = sorted(
            [
                {'feature': label, 'importance': round(float(imp), 4)}
                for label, imp in zip(FEATURE_LABELS, model.feature_importances_)
            ],
            key=lambda x: -x['importance'],
        )

        # Try to evaluate on data if available
        data_path = _find_segmented_csv()
        metrics = {}
        sample_count = 0
        if data_path:
            df = pd.read_csv(data_path, low_memory=False)
            df = df.dropna(subset=['category', 'amount', 'direction']).copy()
            df['transaction_date'] = pd.to_datetime(df['transaction_date'])
            df['amount'] = pd.to_numeric(df['amount'], errors='coerce').abs()
            df = df.dropna(subset=['amount'])
            if not ENCODER_PATH.exists():
                return
            le = joblib.load(ENCODER_PATH)
            df['direction_'] = df['direction'].str.capitalize()
            debits = df[df['direction_'] == 'Debit'].copy()
            if not debits.empty:
                debits['period'] = debits['transaction_date'].dt.to_period('M')
                debits['month'] = debits['transaction_date'].dt.month
                debits['is_weekend'] = debits['transaction_date'].dt.dayofweek.isin([5, 6]).astype(int)
                monthly = (
                    debits.groupby(['period', 'category'])
                    .agg(total_amount=('amount', 'sum'), avg_amount=('amount', 'mean'),
                         transaction_count=('amount', 'count'), month=('month', 'first'),
                         is_weekend_ratio=('is_weekend', 'mean'))
                    .reset_index()
                )
                monthly['period_int'] = monthly['period'].apply(lambda p: p.year * 12 + p.month)
                known = set(le.classes_)
                monthly = monthly[monthly['category'].isin(known)].copy()
                monthly['category_enc'] = le.transform(monthly['category'])
                FEAT = ['period_int', 'category_enc', 'month', 'transaction_count', 'avg_amount', 'is_weekend_ratio']
                X = monthly[FEAT].values
                y = monthly['total_amount'].values
                if len(X) >= 10:
                    _, X_t, _, y_t = train_test_split(X, y, test_size=0.2, random_state=42)
                    y_p = model.predict(X_t)
                    metrics = {
                        'mae':  round(float(mean_absolute_error(y_t, y_p)), 2),
                        'rmse': round(float(np.sqrt(mean_squared_error(y_t, y_p))), 2),
                        'r2':   round(float(r2_score(y_t, y_p)), 4),
                    }
                    sample_count = len(X_t)

        MLModelMetrics.objects.update_or_create(
            model_name='random_forest',
            defaults={
                'metrics': metrics,
                'feature_importance': feature_importance,
                'sample_count': sample_count,
            },
        )
    except Exception:
        pass


def _ensure_classifier_metrics():
    """
    Lazily compute and store LR classifier metrics from the reference dataset
    if not yet recorded. Safe to call on every request (no-op if already stored).
    """
    if MLModelMetrics.objects.filter(model_name='logistic_regression').exists():
        return

    data_path = _find_segmented_csv()
    if data_path is None:
        return

    try:
        from pipeline.categorization.classifier import classify
        from sklearn.metrics import accuracy_score, f1_score, precision_score, recall_score
        from sklearn.model_selection import train_test_split

        df = pd.read_csv(data_path, low_memory=False)
        df = df.dropna(subset=['text_to_segment', 'category']).copy()
        if len(df) < 100:
            return

        _, df_test = train_test_split(df, test_size=0.20, random_state=42, stratify=df['category'])
        result = classify(df_test.copy())
        y_pred = result['category']
        y_true = df_test['category']

        MLModelMetrics.objects.update_or_create(
            model_name='logistic_regression',
            defaults={
                'metrics': {
                    'accuracy':  round(float(accuracy_score(y_true, y_pred)), 4),
                    'f1_weighted': round(float(f1_score(y_true, y_pred, average='weighted', zero_division=0)), 4),
                    'f1_macro':  round(float(f1_score(y_true, y_pred, average='macro', zero_division=0)), 4),
                    'precision': round(float(precision_score(y_true, y_pred, average='weighted', zero_division=0)), 4),
                    'recall':    round(float(recall_score(y_true, y_pred, average='weighted', zero_division=0)), 4),
                },
                'feature_importance': [],
                'sample_count': len(df_test),
            },
        )
    except Exception:
        pass


def _find_segmented_csv() -> Optional[Path]:
    candidates = [
        Path(settings.BASE_DIR) / 'data' / 'processed' / 'transactions_segmentees.csv',
        Path(settings.BASE_DIR).parent / 'data' / 'processed' / 'transactions_segmentees.csv',
    ]
    for p in candidates:
        if p.exists():
            return p
    return None
