"""
Step 1 — Label new CSV files using keyword rules.

For each new CSV, assigns category based on clean_narration + clean_merchant_name
using the same rules as backend/pipeline/categorization/rules.py.
Saves <filename>_labeled.csv to data/processed/.
"""
import sys
from pathlib import Path

import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT / 'backend'))

from pipeline.categorization.rules import CATEGORY_RULES, OTHER_CATEGORY

DATA_DIR = PROJECT_ROOT / 'data' / 'processed'

NEW_FILES = [
    'transactions_high_spending.csv',
    'transactions_ecommerce_heavy.csv',
    'transactions_student_profile.csv',
    'transactions_seasonal_spender.csv',
    'transactions_savings_focused.csv',
    'transactions_low_activity.csv',
    'transactions_high_fraud.csv',
    'transactions_new_user.csv',
]


def _classify_row(text: str) -> str:
    for category, keywords in CATEGORY_RULES:
        if any(kw in text for kw in keywords):
            return category
    return OTHER_CATEGORY


def label_file(filename: str) -> pd.DataFrame:
    path = DATA_DIR / filename
    df = pd.read_csv(path, encoding='utf-8-sig', low_memory=False)

    narration = df.get('clean_narration', df.get('narration', '')).fillna('').str.lower()
    merchant  = df.get('clean_merchant_name', df.get('merchant_name', '')).fillna('').str.lower()
    combined  = (narration + ' ' + merchant).str.strip()

    df['category'] = combined.apply(_classify_row)

    # Build text_to_segment (merchant first, then narration — matches training format)
    df['text_to_segment'] = (merchant + ' ' + narration).str.strip()

    out_name = filename.replace('.csv', '_labeled.csv')
    out_path = DATA_DIR / out_name
    df.to_csv(out_path, index=False, encoding='utf-8-sig')

    n_autre  = (df['category'] == OTHER_CATEGORY).sum()
    print(f'\n{"="*60}')
    print(f'File : {filename}')
    print(f'Rows : {len(df):,}')
    print(f'Category distribution:')
    for cat, cnt in df['category'].value_counts().items():
        flag = '  [NEEDS REVIEW]' if cat == OTHER_CATEGORY else ''
        print(f'  {cat:<30s} {cnt:>5,}{flag}')
    if n_autre:
        print(f'\nSample "Autre" merchants:')
        for m in df[df['category'] == OTHER_CATEGORY]['merchant_name'].dropna().unique()[:10]:
            print(f'  - {m}')
    print(f'Saved -> {out_path.name}')

    return df


if __name__ == '__main__':
    all_dfs = []
    for f in NEW_FILES:
        path = DATA_DIR / f
        if not path.exists():
            print(f'SKIP (not found): {f}')
            continue
        df = label_file(f)
        all_dfs.append(df)

    total_new = sum(len(d) for d in all_dfs)
    print(f'\n{"="*60}')
    print(f'Total new rows labeled: {total_new:,}')
    print('Run retrain_classifier.py next.')
