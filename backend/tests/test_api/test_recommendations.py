import pytest
from django.core.files.uploadedfile import SimpleUploadedFile
from django.urls import reverse

# 6 months of data to give the Random Forest enough to train
CSV_ROWS = ""
for month in range(1, 7):
    m = str(month).zfill(2)
    CSV_ROWS += (
        f"TX{month}01,2024-{m}-01,Credit,5000.00,salaire,Salaire\n"
        f"TX{month}02,2024-{m}-02,Debit,400.00,supermarche,Carrefour\n"
        f"TX{month}03,2024-{m}-03,Debit,60.00,transport careem,Careem\n"
        f"TX{month}04,2024-{m}-04,Debit,3000.00,loyer appartement,Loyer\n"
    )

CSV = "transaction_id,transaction_date,direction,amount,narration,merchant_name\n" + CSV_ROWS


@pytest.fixture
def loaded_client(auth_client):
    f = SimpleUploadedFile('t.csv', CSV.encode(), content_type='text/csv')
    auth_client.post(reverse('upload_csv'), {'file': f}, format='multipart')
    return auth_client


@pytest.mark.django_db
class TestRecommendations:
    def test_recommendations_list(self, loaded_client):
        r = loaded_client.get(reverse('recommendation_list'))
        assert r.status_code == 200
        assert isinstance(r.data, list)

    def test_recommendation_fields(self, loaded_client):
        r = loaded_client.get(reverse('recommendation_list'))
        for rec in r.data:
            assert 'message' in rec
            assert 'priority' in rec
            assert rec['priority'] in ('high', 'medium', 'low')

    def test_predictions_list(self, loaded_client):
        r = loaded_client.get(reverse('prediction_list'))
        assert r.status_code == 200
        assert isinstance(r.data, list)

    def test_predictions_fields(self, loaded_client):
        r = loaded_client.get(reverse('prediction_list'))
        for pred in r.data:
            assert 'category' in pred
            assert 'target_period' in pred
            assert 'predicted_amount' in pred
            assert float(pred['predicted_amount']) >= 0

    def test_predictions_generated_after_upload(self, loaded_client):
        r = loaded_client.get(reverse('prediction_list'))
        assert r.status_code == 200
        assert len(r.data) > 0

    def test_requires_auth(self, client):
        from rest_framework.test import APIClient
        c = APIClient()
        assert c.get(reverse('recommendation_list')).status_code == 401
        assert c.get(reverse('prediction_list')).status_code == 401
