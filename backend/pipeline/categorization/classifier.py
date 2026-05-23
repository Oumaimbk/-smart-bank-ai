import logging
import re
from pathlib import Path

import pandas as pd

logger = logging.getLogger(__name__)

_STORE = Path(__file__).resolve().parent.parent.parent / 'models_store'
_VEC_PATH = _STORE / 'tfidf_vectorizer.pkl'
_CLF_PATH = _STORE / 'lr_category_classifier.pkl'

_vectorizer = None
_classifier = None


def _load_models() -> bool:
    global _vectorizer, _classifier
    if _vectorizer is not None:
        return True
    if not (_VEC_PATH.exists() and _CLF_PATH.exists()):
        return False
    try:
        import joblib
        _vectorizer = joblib.load(_VEC_PATH)
        _classifier = joblib.load(_CLF_PATH)
        logger.info("ML categorization models loaded (TF-IDF + LR).")
        return True
    except Exception as exc:
        logger.warning("Could not load ML models: %s — falling back to rules.", exc)
        _vectorizer = None
        _classifier = None
        return False


def _ml_classify(df: pd.DataFrame) -> pd.DataFrame:
    """TF-IDF + Logistic Regression classification."""
    narration = _get_col(df, 'narration_normalized', 'clean_narration', 'narration')
    merchant  = _get_col(df, 'clean_merchant_name', 'merchant_name')

    text = (merchant + ' ' + narration).str.strip()

    X = _vectorizer.transform(text)
    df['category'] = _classifier.predict(X)
    df['category_confidence'] = _classifier.predict_proba(X).max(axis=1).round(4)
    return df


def _get_col(df: pd.DataFrame, *names: str) -> pd.Series:
    """Return the first existing column among names, or a Series of empty strings."""
    for name in names:
        if name in df.columns:
            return df[name].fillna('').astype(str).str.lower()
    return pd.Series([''] * len(df), index=df.index, dtype=str)


def _rule_classify(df: pd.DataFrame) -> pd.DataFrame:
    """Keyword rule-based classifier. Checks narration AND merchant name."""
    from .rules import CATEGORY_RULES, OTHER_CATEGORY

    narration = _get_col(df, 'narration_normalized', 'clean_narration', 'narration')
    merchant  = _get_col(df, 'clean_merchant_name', 'merchant_name')

    def _match(kw: str, text: str) -> bool:
        # Keywords with special chars (h&m, pull&bear) → substring match
        # Pure-letter keywords (paie, salaire) → word-boundary match to avoid
        # false positives like 'paie' inside 'paiement'
        if re.search(r'[^a-zA-ZÀ-ÿ\s]', kw):
            return kw in text
        return bool(re.search(r'\b' + re.escape(kw) + r'\b', text, re.UNICODE))

    def _classify_row(nar: str, merch: str) -> str:
        text = f"{nar} {merch}"
        for category, keywords in CATEGORY_RULES:
            if any(_match(kw, text) for kw in keywords):
                return category
        return OTHER_CATEGORY

    df['category'] = [_classify_row(n, m) for n, m in zip(narration, merchant)]
    df['category_confidence'] = 1.0
    return df


def classify(df: pd.DataFrame) -> pd.DataFrame:
    """
    Classify transactions into spending categories using a two-step strategy:

    1. Rules first — keyword matching runs on ALL rows.
       Known merchants (H&M, Nike, Amazon, etc.) are always assigned
       the correct category regardless of ML output.

    2. ML fills unknowns — rows where rules returned OTHER_CATEGORY
       go through TF-IDF + Logistic Regression if the model is available.
       This handles the long tail of narrations not covered by rules.

    Output: same DataFrame with 'category' and 'category_confidence' added.
    """
    df = df.copy()

    # Step 1: rules pre-filter on all rows
    df = _rule_classify(df)

    # Step 2: ML fills rows that rules couldn't classify
    if _load_models():
        from .rules import OTHER_CATEGORY
        unknown_mask = df['category'] == OTHER_CATEGORY
        if unknown_mask.any():
            ml_result = _ml_classify(df[unknown_mask].copy())
            df.loc[unknown_mask, 'category'] = ml_result['category'].values
            df.loc[unknown_mask, 'category_confidence'] = ml_result['category_confidence'].values

    return df
