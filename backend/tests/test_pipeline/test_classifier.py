import pandas as pd
import pytest

from pipeline.categorization.classifier import classify
from pipeline.categorization.rules import OTHER_CATEGORY


@pytest.fixture
def sample_df():
    return pd.DataFrame({
        'transaction_id': ['TX001', 'TX002', 'TX003', 'TX004'],
        'direction': ['Credit', 'Debit', 'Debit', 'Debit'],
        'amount': [5000.0, 25.0, 300.0, 100.0],
        'narration': ['virement employeur', 'TRANSPORT CAREEM', 'CARREFOUR MARJANE', 'unknown payment'],
        'narration_normalized': ['VIREMENT EMPLOYEUR', 'TRANSPORT CAREEM', 'CARREFOUR MARJANE', 'UNKNOWN PAYMENT'],
        'merchant_name': ['Salaire', 'Careem', 'Carrefour', ''],
    })


def test_salary_categorized_correctly(sample_df):
    result = classify(sample_df)
    # ML model maps salary/virement transactions to 'Revenu'
    assert result.loc[0, 'category'] == 'Revenu'


def test_transport_categorized_correctly(sample_df):
    result = classify(sample_df)
    assert result.loc[1, 'category'] == 'Transport'


def test_alimentation_categorized_correctly(sample_df):
    result = classify(sample_df)
    assert result.loc[2, 'category'] == 'Alimentation'


def test_unknown_gets_a_category(sample_df):
    result = classify(sample_df)
    # ML model always assigns a category; rule fallback would return OTHER_CATEGORY
    assert result.loc[3, 'category'] in (OTHER_CATEGORY, 'Transport', 'Alimentation',
                                          'Logement', 'Loisirs', 'Shopping', 'Santé',
                                          'Retrait cash', 'Revenu', 'Factures',
                                          'E-commerce', 'Voyage', 'Banque & Finance',
                                          'Télécommunications', 'Épargne & Placement')


def test_all_rows_have_category(sample_df):
    result = classify(sample_df)
    assert result['category'].notna().all()
    assert (result['category'] != '').all()
