import pytest
from django.core.files.uploadedfile import SimpleUploadedFile
from django.urls import reverse


CSV = (
    "transaction_id,transaction_date,direction,amount,narration,merchant_name\n"
    "TX001,2024-01-01,Credit,5000.00,salaire,Salaire\n"
    "TX002,2024-01-02,Debit,200.00,CARREFOUR MARJANE,Carrefour\n"
    "TX003,2024-01-03,Debit,50.00,TRANSPORT CAREEM,Careem\n"
    "TX004,2024-02-01,Credit,5000.00,salaire,Salaire\n"
    "TX005,2024-02-02,Debit,300.00,CARREFOUR MARJANE,Carrefour\n"
    "TX006,2024-02-03,Debit,80.00,TRANSPORT CAREEM,Careem\n"
)


@pytest.fixture
def loaded_client(auth_client):
    f = SimpleUploadedFile('t.csv', CSV.encode(), content_type='text/csv')
    auth_client.post(reverse('upload_csv'), {'file': f}, format='multipart')
    return auth_client


@pytest.mark.django_db
class TestAnalytics:
    def test_kpi_structure(self, loaded_client):
        r = loaded_client.get(reverse('kpi'))
        assert r.status_code == 200
        for key in ('total_credit', 'total_debit', 'net_balance', 'transaction_count'):
            assert key in r.data

    def test_kpi_values(self, loaded_client):
        r = loaded_client.get(reverse('kpi'))
        assert r.data['total_credit'] == 10000.0
        assert r.data['total_debit'] == 630.0
        assert r.data['transaction_count'] == 6

    def test_kpi_empty_user(self, auth_client):
        r = auth_client.get(reverse('kpi'))
        assert r.status_code == 200
        assert r.data['transaction_count'] == 0

    def test_spending_by_category_returns_list(self, loaded_client):
        r = loaded_client.get(reverse('spending_by_category'))
        assert r.status_code == 200
        assert isinstance(r.data, list)
        for item in r.data:
            assert 'category' in item
            assert 'total' in item

    def test_spending_only_debits(self, loaded_client):
        r = loaded_client.get(reverse('spending_by_category'))
        # Salaire is a Credit — must not appear in spending
        categories = [d['category'] for d in r.data]
        assert 'Salaire' not in categories

    def test_monthly_evolution_structure(self, loaded_client):
        r = loaded_client.get(reverse('monthly_evolution'))
        assert r.status_code == 200
        assert isinstance(r.data, list)
        assert len(r.data) > 0
        for item in r.data:
            assert 'month' in item
            assert 'direction' in item
            assert 'total' in item

    def test_top_merchants_max_10(self, loaded_client):
        r = loaded_client.get(reverse('top_merchants'))
        assert r.status_code == 200
        assert len(r.data) <= 10

    def test_analytics_requires_auth(self, client):
        from rest_framework.test import APIClient
        c = APIClient()
        assert c.get(reverse('kpi')).status_code == 401
        assert c.get(reverse('spending_by_category')).status_code == 401
        assert c.get(reverse('monthly_evolution')).status_code == 401
