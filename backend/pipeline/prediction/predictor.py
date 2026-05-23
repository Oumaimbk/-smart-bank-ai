import numpy as np
import joblib
import pandas as pd

from .trainer import ENCODER_PATH, FEATURE_COLS, MODEL_PATH, model_exists


def predict_next_month(df: pd.DataFrame) -> list[dict]:
    """
    Load the global Random Forest and predict next-month spending
    for each category present in the user's debit transactions.
    Features must match those used in trainer.py (FEATURE_COLS).
    """
    if not model_exists():
        return []

    model = joblib.load(MODEL_PATH)
    le    = joblib.load(ENCODER_PATH)

    debits = df[df['direction'] == 'Debit'].copy()
    debits['transaction_date'] = pd.to_datetime(debits['transaction_date'])

    latest_date     = debits['transaction_date'].max()
    next_month_date = latest_date + pd.DateOffset(months=1)
    next_period_int = next_month_date.year * 12 + next_month_date.month
    next_month_num  = next_month_date.month
    target_period   = next_month_date.strftime('%Y-%m')

    # Last-month stats per category (used as proxy for next month)
    cutoff = latest_date - pd.DateOffset(months=1)
    last_month = debits[debits['transaction_date'] >= cutoff]
    stats = (
        last_month.groupby('category')
        .agg(transaction_count=('amount', 'count'), avg_amount=('amount', 'mean'))
    )

    known = set(le.classes_)
    predictions = []

    for category in debits['category'].unique():
        if category not in known:
            continue

        cat_enc   = int(le.transform([category])[0])
        txn_count = float(stats.loc[category, 'transaction_count']) if category in stats.index else 1.0
        avg_amt   = float(stats.loc[category, 'avg_amount'])        if category in stats.index else 0.0
        is_weekend_ratio = 0.286  # ~2/7 weekend days

        X = np.array([[next_period_int, cat_enc, next_month_num, txn_count, avg_amt, is_weekend_ratio]])
        predicted = float(model.predict(X)[0])
        predictions.append({
            'category':         category,
            'target_period':    target_period,
            'predicted_amount': round(max(predicted, 0.0), 2),
        })

    return predictions
