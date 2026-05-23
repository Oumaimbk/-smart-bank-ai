import pandas as pd


def clean(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()

    df = df.drop_duplicates(subset=['transaction_id'])

    df['transaction_date'] = pd.to_datetime(df['transaction_date'], errors='coerce')
    df = df.dropna(subset=['transaction_date'])

    df['amount'] = pd.to_numeric(df['amount'], errors='coerce').abs()
    df = df.dropna(subset=['amount'])

    df['direction'] = df['direction'].astype(str).str.strip().str.capitalize()
    df = df[df['direction'].isin(['Credit', 'Debit'])]

    if 'transaction_time' in df.columns:
        df['transaction_time'] = pd.to_datetime(
            df['transaction_time'], format='%H:%M', errors='coerce'
        ).dt.time

    if 'balance_after' in df.columns:
        df['balance_after'] = pd.to_numeric(df['balance_after'], errors='coerce')

    str_cols = [
        'customer_id', 'account_type', 'payment_method',
        'narration', 'merchant_name', 'merchant_city', 'merchant_country',
    ]
    for col in str_cols:
        if col in df.columns:
            df[col] = df[col].fillna('').astype(str).str.strip()

    return df.reset_index(drop=True)
