import pandas as pd
from django.db import transaction as db_transaction
from django.utils import timezone

from apps.anomalies.models import Anomaly
from apps.recommendations.models import Prediction, Recommendation
from apps.transactions.models import Transaction, UploadBatch
from pipeline.anomaly_detection.detector import detect
from pipeline.categorization.classifier import classify
from pipeline.ingestion.loader import load_csv, validate_columns
from pipeline.prediction.predictor import predict_next_month
from pipeline.prediction.trainer import train
from pipeline.preprocessing.cleaner import clean
from pipeline.preprocessing.feature_engineering import engineer_features
from pipeline.preprocessing.normalizer import normalize
from pipeline.recommendations.engine import generate


class PipelineError(Exception):
    pass


class PipelineService:

    @staticmethod
    @db_transaction.atomic
    def run(file_obj, user, filename: str) -> dict:
        batch = UploadBatch.objects.create(
            user=user, filename=filename, status=UploadBatch.STATUS_PROCESSING
        )

        try:
            # 1. Ingest
            df = load_csv(file_obj)
            missing = validate_columns(df)
            if missing:
                raise PipelineError(f"Missing required columns: {', '.join(missing)}")

            # 2. Preprocess
            df = clean(df)
            df = normalize(df)
            df = engineer_features(df)

            # 3. Categorize
            df = classify(df)

            if df.empty:
                raise PipelineError("No valid transactions found after cleaning.")

            # 4. Skip already-imported transaction IDs for this user
            existing_ids = set(
                Transaction.objects.filter(user=user)
                .values_list('transaction_id', flat=True)
            )

            new_rows = df[~df['transaction_id'].isin(existing_ids)]

            transactions_to_create = [
                Transaction(
                    user=user,
                    batch=batch,
                    transaction_id=row['transaction_id'],
                    customer_id=row.get('customer_id', ''),
                    transaction_date=row['transaction_date'].date(),
                    transaction_time=_safe_time(row.get('transaction_time')),
                    account_type=row.get('account_type', ''),
                    payment_method=row.get('payment_method', ''),
                    direction=row['direction'],
                    amount=row['amount'],
                    balance_after=_safe_decimal(row.get('balance_after')),
                    narration=row.get('narration', ''),
                    merchant_name=row.get('merchant_name', ''),
                    merchant_city=row.get('merchant_city', ''),
                    merchant_country=row.get('merchant_country', ''),
                    category=row['category'],
                )
                for _, row in new_rows.iterrows()
            ]

            Transaction.objects.bulk_create(transactions_to_create)

            # 5. Detect anomalies on new rows only
            anomaly_results = detect(new_rows)
            txn_map = {
                t.transaction_id: t for t in Transaction.objects.filter(user=user, batch=batch)
            }
            Anomaly.objects.bulk_create([
                Anomaly(
                    transaction=txn_map[a['transaction_id']],
                    anomaly_type=a['anomaly_type'],
                    score=a['score'],
                    description=a['description'],
                )
                for a in anomaly_results
                if a['transaction_id'] in txn_map
            ], ignore_conflicts=True)

            # Build anomaly summary by category for recommendations
            tx_to_cat = new_rows.set_index('transaction_id')['category'].to_dict() if 'category' in new_rows.columns else {}
            anomaly_by_cat: dict[str, int] = {}
            for a in anomaly_results:
                cat = tx_to_cat.get(a['transaction_id'], '')
                if cat:
                    anomaly_by_cat[cat] = anomaly_by_cat.get(cat, 0) + 1
            anomaly_summary = {'total': len(anomaly_results), 'by_category': anomaly_by_cat}

            # 6. Retrain global model on all of this user's data
            all_txns = list(
                Transaction.objects
                .filter(user=user)
                .values('transaction_id', 'transaction_date', 'direction', 'amount', 'category')
            )
            all_df = pd.DataFrame(all_txns)
            all_df['transaction_date'] = pd.to_datetime(all_df['transaction_date'])
            train(all_df)

            # 7. Predict next month
            predictions = predict_next_month(all_df)
            Prediction.objects.filter(user=user).delete()
            Prediction.objects.bulk_create([Prediction(user=user, **p) for p in predictions])

            # 8. Generate recommendations
            recommendations = generate(all_df, predictions, anomaly_summary)
            Recommendation.objects.filter(user=user).delete()
            Recommendation.objects.bulk_create([
                Recommendation(
                    user=user,
                    category=r.get('category', ''),
                    message=r['message'],
                    reason=r.get('reason', ''),
                    priority=r['priority'],
                )
                for r in recommendations
            ])

            # 9. Finalise batch
            batch.status = UploadBatch.STATUS_COMPLETED
            batch.transaction_count = len(transactions_to_create)
            batch.processed_at = timezone.now()
            batch.save()

            return {
                'batch_id': batch.id,
                'new_transactions': len(transactions_to_create),
                'skipped_duplicates': len(df) - len(new_rows),
                'anomalies_detected': len(anomaly_results),
                'predictions_generated': len(predictions),
                'recommendations_generated': len(recommendations),
            }

        except PipelineError:
            batch.status = UploadBatch.STATUS_FAILED
            batch.save()
            raise

        except Exception as exc:
            batch.status = UploadBatch.STATUS_FAILED
            batch.error_message = str(exc)
            batch.save()
            raise PipelineError(f"Pipeline failed: {exc}") from exc


def _safe_time(val):
    if val is None:
        return None
    try:
        if pd.isna(val):
            return None
    except (TypeError, ValueError):
        pass
    return val


def _safe_decimal(val):
    if val is None:
        return None
    try:
        if pd.isna(val):
            return None
    except (TypeError, ValueError):
        pass
    return val
