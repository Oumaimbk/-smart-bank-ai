"""
Steps 2 + 3 — Merge labeled data and retrain TF-IDF + LR classifier.

Usage:
    cd PE
    python notebooks/retrain_classifier.py

Produces:
    data/processed/transactions_enriched.csv
    backend/models_store/tfidf_vectorizer.pkl   (overwrites)
    backend/models_store/lr_category_classifier.pkl (overwrites)
"""
import sys
from pathlib import Path

import joblib
import numpy as np
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    accuracy_score,
    classification_report,
    confusion_matrix,
)
from sklearn.model_selection import train_test_split

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR     = PROJECT_ROOT / 'data' / 'processed'
MODELS_STORE = PROJECT_ROOT / 'backend' / 'models_store'

ORIGINAL_CSV = DATA_DIR / 'transactions_segmentees.csv'
ENRICHED_CSV = DATA_DIR / 'transactions_enriched.csv'

LABELED_FILES = [
    'transactions_high_spending_labeled.csv',
    'transactions_ecommerce_heavy_labeled.csv',
    'transactions_student_profile_labeled.csv',
    'transactions_seasonal_spender_labeled.csv',
    'transactions_savings_focused_labeled.csv',
    'transactions_low_activity_labeled.csv',
    'transactions_high_fraud_labeled.csv',
    'transactions_new_user_labeled.csv',
]

REQUIRED_COLS = ['text_to_segment', 'category']
DROP_CATEGORIES = {'Autre', '', None}


# ── Step 2: Merge ─────────────────────────────────────────────────────────────

def load_original() -> pd.DataFrame:
    df = pd.read_csv(ORIGINAL_CSV, low_memory=False)
    # Original uses text_to_segment directly
    df = df[['text_to_segment', 'category']].copy()
    return df


def load_labeled(filename: str):
    path = DATA_DIR / filename
    if not path.exists():
        print(f'  SKIP (not found): {filename}')
        return None
    df = pd.read_csv(path, encoding='utf-8-sig', low_memory=False)
    if 'text_to_segment' not in df.columns:
        merchant  = df.get('clean_merchant_name', df.get('merchant_name', '')).fillna('').str.lower()
        narration = df.get('clean_narration',     df.get('narration', '')).fillna('').str.lower()
        df['text_to_segment'] = (merchant + ' ' + narration).str.strip()
    return df[['text_to_segment', 'category']].copy()


def merge_datasets() -> pd.DataFrame:
    print('\n-- Step 2: Merging datasets ---')
    frames = [load_original()]
    print(f'  Original    : {len(frames[0]):>8,} rows')

    for fname in LABELED_FILES:
        df = load_labeled(fname)
        if df is not None:
            print(f'  {fname:<45s}: {len(df):>6,} rows')
            frames.append(df)

    merged = pd.concat(frames, ignore_index=True)
    merged = merged.dropna(subset=['text_to_segment', 'category'])
    merged = merged[~merged['category'].isin(DROP_CATEGORIES)]
    merged = merged[merged['text_to_segment'].str.strip() != '']
    # Keep all rows — repeated narrations are valid training signal for the classifier

    merged.to_csv(ENRICHED_CSV, index=False, encoding='utf-8')

    print(f'\n  Total rows  : {len(merged):>8,}')
    print(f'\n  Category distribution:')
    for cat, cnt in merged['category'].value_counts().items():
        pct = cnt / len(merged) * 100
        print(f'    {cat:<35s} {cnt:>6,}  ({pct:.1f}%)')
    print(f'\n  Saved -> {str(ENRICHED_CSV)}')
    return merged


# ── Step 3: Train ──────────────────────────────────────────────────────────────

def train_model(merged: pd.DataFrame) -> None:
    print('\n-- Step 3: Training TF-IDF + Logistic Regression ---')

    X = merged['text_to_segment'].astype(str)
    y = merged['category']

    # Ensure every class has at least 2 samples for stratified split
    min_samples = y.value_counts().min()
    test_size   = 0.20 if min_samples >= 10 else 0.10

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=test_size, random_state=42, stratify=y
    )
    print(f'  Train: {len(X_train):,}  |  Test: {len(X_test):,}')

    vectorizer = TfidfVectorizer(
        ngram_range=(1, 2),
        max_features=10_000,
        sublinear_tf=True,
        strip_accents='unicode',
        analyzer='word',
        token_pattern=r'(?u)\b\w+\b',
    )
    X_train_tfidf = vectorizer.fit_transform(X_train)
    X_test_tfidf  = vectorizer.transform(X_test)

    clf = LogisticRegression(
        max_iter=1000,
        C=5.0,
        solver='lbfgs',
        multi_class='multinomial',
        class_weight='balanced',
        random_state=42,
        n_jobs=-1,
    )
    clf.fit(X_train_tfidf, y_train)

    y_pred = clf.predict(X_test_tfidf)
    acc    = accuracy_score(y_test, y_pred)

    print(f'\n  Accuracy: {acc * 100:.2f}%')
    print(f'\n{classification_report(y_test, y_pred, digits=4, zero_division=0)}')

    # Save models
    MODELS_STORE.mkdir(parents=True, exist_ok=True)
    joblib.dump(vectorizer, MODELS_STORE / 'tfidf_vectorizer.pkl')
    joblib.dump(clf,        MODELS_STORE / 'lr_category_classifier.pkl')
    print(f'  Models saved to {str(MODELS_STORE)}')

    return acc


# -- Step 4: Quick verification ---────────────────────────────────

def verify_model() -> None:
    print('\n-- Step 4: Quick verification ------------------')
    sys.path.insert(0, str(PROJECT_ROOT / 'backend'))

    # Force reload of cached model
    import pipeline.categorization.classifier as clf_module
    clf_module._vectorizer = None
    clf_module._classifier = None

    from pipeline.categorization.classifier import classify

    test_rows = [
        {'clean_narration': 'PAIEMENT HM',          'clean_merchant_name': 'H&M'},
        {'clean_narration': 'PAIEMENT NIKE',         'clean_merchant_name': 'Nike'},
        {'clean_narration': 'PAIEMENT ZARA',         'clean_merchant_name': 'Zara'},
        {'clean_narration': 'AMAZON PAYMENTS',       'clean_merchant_name': 'Amazon'},
        {'clean_narration': 'JUMIA COMMANDE',        'clean_merchant_name': 'Jumia'},
        {'clean_narration': 'ACHAT FNAC',            'clean_merchant_name': 'Fnac'},
        {'clean_narration': 'SEPHORA COSMETIQUE',    'clean_merchant_name': 'Sephora'},
        {'clean_narration': 'GLOVO DELIVERY',        'clean_merchant_name': 'Glovo'},
        {'clean_narration': 'VIREMENT SALAIRE',      'clean_merchant_name': 'Salaire'},
        {'clean_narration': 'ACHAT BIM',             'clean_merchant_name': 'BIM'},
        {'clean_narration': 'CARBURANT SHELL',       'clean_merchant_name': 'Shell'},
        {'clean_narration': 'TRANSPORT CAREEM RABAT','clean_merchant_name': 'Careem'},
    ]

    df = pd.DataFrame(test_rows)
    result = classify(df)

    print(f'\n  {"Merchant":<22} {"-":>2} {"Category":<22} Confidence')
    print(f'  {"-"*60}')
    for _, row in result.iterrows():
        conf_flag = '' if row['category_confidence'] >= 0.80 else '  [LOW]'
        print(f'  {row["clean_merchant_name"]:<22} -> {row["category"]:<22} {row["category_confidence"]:.2f}{conf_flag}')


if __name__ == '__main__':
    merged = merge_datasets()
    train_model(merged)
    verify_model()
    print('\nDone. Run: docker compose restart backend')
