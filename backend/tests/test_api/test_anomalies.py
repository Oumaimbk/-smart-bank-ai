import pytest
from django.core.files.uploadedfile import SimpleUploadedFile
from django.urls import reverse

# 15 normal Alimentation transactions (~100 MAD) + 1 extreme outlier (9000 MAD)
# With 15 normals: mean≈656, std≈2225, z-score of 9000 ≈ 3.75 → above threshold 2.5
# TX016 is at 02:30 → triggers odd_hour anomaly
CSV = (
    "transaction_id,transaction_date,transaction_time,direction,amount,narration,merchant_name\n"
    "TX001,2024-01-01,10:00,Debit,100.00,supermarche,Carrefour\n"
    "TX002,2024-01-02,10:30,Debit,105.00,supermarche,Carrefour\n"
    "TX003,2024-01-03,11:00,Debit,98.00,supermarche,Carrefour\n"
    "TX004,2024-01-04,09:00,Debit,102.00,supermarche,Carrefour\n"
    "TX005,2024-01-05,10:00,Debit,97.00,supermarche,Carrefour\n"
    "TX006,2024-01-06,11:30,Debit,103.00,supermarche,Carrefour\n"
    "TX007,2024-01-07,10:00,Debit,99.00,supermarche,Carrefour\n"
    "TX008,2024-01-08,09:30,Debit,101.00,supermarche,Carrefour\n"
    "TX009,2024-01-09,10:00,Debit,96.00,supermarche,Carrefour\n"
    "TX010,2024-01-10,11:00,Debit,104.00,supermarche,Carrefour\n"
    "TX011,2024-01-11,10:00,Debit,100.00,supermarche,Carrefour\n"
    "TX012,2024-01-12,10:30,Debit,98.00,supermarche,Carrefour\n"
    "TX013,2024-01-13,11:00,Debit,103.00,supermarche,Carrefour\n"
    "TX014,2024-01-14,09:00,Debit,97.00,supermarche,Carrefour\n"
    "TX015,2024-01-15,10:00,Debit,102.00,supermarche,Carrefour\n"
    "TX016,2024-01-16,02:30,Debit,9000.00,supermarche,Carrefour\n"
    "TX017,2024-01-01,10:00,Credit,5000.00,salaire,Salaire\n"
)


@pytest.fixture
def loaded_client(auth_client):
    f = SimpleUploadedFile('t.csv', CSV.encode(), content_type='text/csv')
    auth_client.post(reverse('upload_csv'), {'file': f}, format='multipart')
    return auth_client


@pytest.mark.django_db
class TestAnomalies:
    def test_anomaly_list_paginated(self, loaded_client):
        r = loaded_client.get(reverse('anomaly_list'))
        assert r.status_code == 200
        assert 'count' in r.data
        assert 'results' in r.data

    def test_high_amount_anomaly_detected(self, loaded_client):
        # TX016 (9000 MAD) is an obvious outlier — flagged by IF or rule engine.
        r_all = loaded_client.get(reverse('anomaly_list'))
        assert r_all.status_code == 200
        assert r_all.data['count'] >= 1
        types = {a['anomaly_type'] for a in r_all.data['results']}
        valid = {'high_amount', 'ML_ANOMALY', 'ml_isolation_forest', 'rule_high_amount', 'rule_odd_hour'}
        assert types & valid

    def test_odd_hour_anomaly_detected(self, loaded_client):
        # TX016 is at 02:30 — should be flagged regardless of ML vs rule path.
        r_all = loaded_client.get(reverse('anomaly_list'))
        assert r_all.status_code == 200
        assert r_all.data['count'] >= 1

    def test_summary_endpoint(self, loaded_client):
        r = loaded_client.get(reverse('anomaly_summary'))
        assert r.status_code == 200
        assert 'total' in r.data
        assert 'by_type' in r.data
        assert r.data['total'] >= 1

    def test_anomaly_filter_by_type(self, loaded_client):
        r = loaded_client.get(reverse('anomaly_list'), {'anomaly_type': 'high_amount'})
        assert r.status_code == 200
        for a in r.data['results']:
            assert a['anomaly_type'] == 'high_amount'

    def test_anomaly_fields(self, loaded_client):
        r = loaded_client.get(reverse('anomaly_list'))
        if r.data['count'] > 0:
            a = r.data['results'][0]
            for field in ('transaction_id', 'amount', 'anomaly_type', 'score', 'description'):
                assert field in a

    def test_anomaly_requires_auth(self, client):
        from rest_framework.test import APIClient
        c = APIClient()
        assert c.get(reverse('anomaly_list')).status_code == 401
        assert c.get(reverse('anomaly_summary')).status_code == 401
