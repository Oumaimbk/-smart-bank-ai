import pandas as pd


def engineer_features(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df['year'] = df['transaction_date'].dt.year
    df['month'] = df['transaction_date'].dt.month
    df['day_of_week'] = df['transaction_date'].dt.dayofweek
    df['is_weekend'] = df['day_of_week'].isin([5, 6]).astype(int)

    if 'transaction_time' in df.columns:
        df['hour'] = df['transaction_time'].apply(
            lambda t: t.hour if pd.notna(t) and t is not None else None
        )
    else:
        df['hour'] = None

    return df
