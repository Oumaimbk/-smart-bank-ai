import pandas as pd

REQUIRED_COLUMNS = {
    'transaction_id',
    'transaction_date',
    'direction',
    'amount',
}


def load_csv(file_obj) -> pd.DataFrame:
    return pd.read_csv(file_obj, encoding='utf-8', on_bad_lines='skip')


def validate_columns(df: pd.DataFrame) -> list[str]:
    return [col for col in REQUIRED_COLUMNS if col not in df.columns]
