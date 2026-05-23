import pandas as pd
import pytest

from pipeline.preprocessing.cleaner import clean


@pytest.fixture
def raw_df():
    return pd.DataFrame({
        'transaction_id': ['TX001', 'TX001', 'TX002', 'TX003'],
        'customer_id': ['C1', 'C1', 'C1', 'C1'],
        'transaction_date': ['2024-01-01', '2024-01-01', 'not-a-date', '2024-01-03'],
        'transaction_time': ['09:30', '09:30', '10:00', '11:00'],
        'direction': ['Debit', 'Debit', 'Credit', 'DEBIT'],
        'amount': ['100.5', '100.5', 'bad', '200.0'],
        'narration': ['coffee', 'coffee', 'salary', 'groceries'],
    })


def test_removes_duplicates(raw_df):
    result = clean(raw_df)
    assert result['transaction_id'].nunique() == len(result)


def test_drops_invalid_dates(raw_df):
    result = clean(raw_df)
    assert result['transaction_date'].notna().all()


def test_drops_invalid_amounts(raw_df):
    result = clean(raw_df)
    assert pd.to_numeric(result['amount'], errors='coerce').notna().all()


def test_normalizes_direction_case(raw_df):
    result = clean(raw_df)
    assert set(result['direction'].unique()).issubset({'Credit', 'Debit'})


def test_amount_is_positive(raw_df):
    result = clean(raw_df)
    assert (result['amount'] >= 0).all()
