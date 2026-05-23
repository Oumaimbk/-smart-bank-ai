from pathlib import Path

import joblib
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder

_STORE = Path(__file__).resolve().parent.parent.parent / 'models_store'
MODEL_PATH   = _STORE / 'rf_expense_predictor.pkl'
ENCODER_PATH = _STORE / 'category_encoder.pkl'

MIN_TRAINING_ROWS = 10

FEATURE_COLS = ['period_int', 'category_enc', 'month', 'transaction_count', 'avg_amount', 'is_weekend_ratio']
FEATURE_LABELS = ['Période', 'Catégorie', 'Mois', 'Nb transactions', 'Montant moyen', 'Ratio week-end']


def model_exists() -> bool:
    return MODEL_PATH.exists() and ENCODER_PATH.exists()


def _build_monthly_features(df: pd.DataFrame) -> pd.DataFrame:
    debits = df[df['direction'] == 'Debit'].copy()
    debits['transaction_date'] = pd.to_datetime(debits['transaction_date'])
    debits['period']     = debits['transaction_date'].dt.to_period('M')
    debits['month']      = debits['transaction_date'].dt.month
    debits['is_weekend'] = debits['transaction_date'].dt.dayofweek.isin([5, 6]).astype(int)

    monthly = (
        debits.groupby(['period', 'category'])
        .agg(
            total_amount      = ('amount', 'sum'),
            avg_amount        = ('amount', 'mean'),
            transaction_count = ('amount', 'count'),
            month             = ('month', 'first'),
            is_weekend_ratio  = ('is_weekend', 'mean'),
        )
        .reset_index()
    )
    monthly['period_int'] = monthly['period'].apply(lambda p: p.year * 12 + p.month)
    return monthly


def train(df: pd.DataFrame) -> None:
    """
    Train a Random Forest Regressor on monthly spending per category.
    Evaluates on a 20 % holdout split and persists metrics + feature
    importances to the MLModelMetrics table.
    """
    monthly = _build_monthly_features(df)
    if len(monthly) < MIN_TRAINING_ROWS:
        return

    le = LabelEncoder()
    monthly['category_enc'] = le.fit_transform(monthly['category'])

    X = monthly[FEATURE_COLS].values
    y = monthly['total_amount'].values

    if len(X) >= 20:
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.20, random_state=42
        )
    else:
        X_train, X_test, y_train, y_test = X, X, y, y

    model = RandomForestRegressor(
        n_estimators=200,
        max_depth=10,
        min_samples_leaf=2,
        random_state=42,
        n_jobs=-1,
    )
    model.fit(X_train, y_train)

    y_pred = model.predict(X_test)
    mae  = float(mean_absolute_error(y_test, y_pred))
    rmse = float(np.sqrt(mean_squared_error(y_test, y_pred)))
    r2   = float(r2_score(y_test, y_pred))

    feature_importance = sorted(
        [
            {'feature': label, 'importance': round(float(imp), 4)}
            for label, imp in zip(FEATURE_LABELS, model.feature_importances_)
        ],
        key=lambda x: -x['importance'],
    )

    _STORE.mkdir(parents=True, exist_ok=True)
    joblib.dump(model, MODEL_PATH)
    joblib.dump(le, ENCODER_PATH)

    _save_metrics(mae, rmse, r2, feature_importance, sample_count=len(X_test))


def _save_metrics(mae, rmse, r2, feature_importance, sample_count):
    try:
        from apps.analytics.models import MLModelMetrics
        MLModelMetrics.objects.update_or_create(
            model_name='random_forest',
            defaults={
                'metrics': {
                    'mae':  round(mae, 2),
                    'rmse': round(rmse, 2),
                    'r2':   round(r2, 4),
                },
                'feature_importance': feature_importance,
                'sample_count': sample_count,
            },
        )
    except Exception:
        pass
