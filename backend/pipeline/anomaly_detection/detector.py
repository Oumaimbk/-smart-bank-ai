import logging
from pathlib import Path

import numpy as np
import pandas as pd

logger = logging.getLogger(__name__)

_STORE = Path(__file__).resolve().parent.parent.parent / 'models_store'
_ISO_PATH = _STORE / 'isolation_forest.pkl'
_ENC_PATH = _STORE / 'anomaly_label_encoder.pkl'

_iso_forest = None
_label_encoder = None

_ZSCORE_THRESHOLD = 2.5
_ODD_HOUR_RANGE = range(0, 6)


def _load_models() -> bool:
    global _iso_forest, _label_encoder
    if _iso_forest is not None:
        return True
    if not (_ISO_PATH.exists() and _ENC_PATH.exists()):
        return False
    try:
        import joblib
        _iso_forest = joblib.load(_ISO_PATH)
        _label_encoder = joblib.load(_ENC_PATH)
        logger.info("Isolation Forest anomaly detection model loaded.")
        return True
    except Exception as exc:
        logger.warning("Could not load Isolation Forest: %s", exc)
        _iso_forest = None
        _label_encoder = None
        return False


def _ml_detect(df: pd.DataFrame) -> list[dict]:
    """Isolation Forest — unusual spending pattern detection."""
    debits = df[df['direction'] == 'Debit'].copy()
    if debits.empty:
        return []

    known = set(_label_encoder.classes_)
    fallback_cat = _label_encoder.classes_[0]
    safe_cat = debits['category'].apply(lambda c: c if c in known else fallback_cat)
    cat_enc = _label_encoder.transform(safe_cat).astype(float)

    hour = debits.get('hour', pd.Series(12, index=debits.index)).fillna(12).astype(float)
    is_weekend = debits.get('is_weekend', pd.Series(0, index=debits.index)).fillna(0).astype(float)

    X = np.column_stack([
        debits['amount'].astype(float).values,
        hour.values,
        is_weekend.values,
        cat_enc,
    ])

    preds = _iso_forest.predict(X)
    scores = _iso_forest.score_samples(X)

    anomalies = []
    for i, (_, row) in enumerate(debits.iterrows()):
        if preds[i] == -1:
            score = round(float(-scores[i]), 4)
            anomalies.append({
                'transaction_id': row['transaction_id'],
                'anomaly_type': 'ml_isolation_forest',
                'score': score,
                'description': (
                    f"Isolation Forest a identifié cette transaction "
                    f"{row.get('category', '')} ({float(row['amount']):.2f} MAD) "
                    f"comme un schéma de dépense inhabituel (score: {score})."
                ),
            })
    return anomalies


def _rule_detect(df: pd.DataFrame) -> list[dict]:
    """Rule-based supplementary detection: z-score high amount + odd hour."""
    anomalies: list[dict] = []
    debits = df[df['direction'] == 'Debit'].copy()
    if debits.empty:
        return anomalies

    for category, group in debits.groupby('category'):
        if len(group) < 3:
            continue
        mean = group['amount'].mean()
        std = group['amount'].std()
        if std == 0:
            continue
        zscores = (group['amount'] - mean) / std
        for idx, z in zscores.items():
            if z > _ZSCORE_THRESHOLD:
                row = df.loc[idx]
                anomalies.append({
                    'transaction_id': row['transaction_id'],
                    'anomaly_type': 'rule_high_amount',
                    'score': round(float(z), 4),
                    'description': (
                        f"Montant {float(row['amount']):.2f} MAD anormalement élevé pour "
                        f"'{category}' (moyenne: {mean:.2f} MAD, z-score: {z:.2f})."
                    ),
                })

    hour_col = df.get('hour') if 'hour' in df.columns else None
    if hour_col is not None:
        for _, row in df[df['hour'].isin(_ODD_HOUR_RANGE)].iterrows():
            anomalies.append({
                'transaction_id': row['transaction_id'],
                'anomaly_type': 'rule_odd_hour',
                'score': 1.0,
                'description': (
                    f"Transaction à {int(row['hour'])}h — "
                    f"en dehors des horaires bancaires habituels (00h–05h59)."
                ),
            })
    return anomalies


def detect(df: pd.DataFrame) -> list[dict]:
    """
    Detect unusual spending patterns using two complementary methods:

    1. Isolation Forest (ML) — flags statistically unusual transactions
       based on amount, hour, weekend, and category features.
    2. Rule-based engine — flags transactions with extremely high z-scores
       within their category, or at unusual hours (00:00–05:59).

    Both methods run simultaneously. A transaction may be flagged by
    one or both methods, each with its own anomaly_type and score.
    """
    anomalies: list[dict] = []

    if _load_models():
        anomalies.extend(_ml_detect(df))

    anomalies.extend(_rule_detect(df))

    return anomalies
