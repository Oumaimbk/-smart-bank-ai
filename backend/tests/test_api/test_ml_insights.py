import pytest
from django.core.files.uploadedfile import SimpleUploadedFile
from django.urls import reverse

# 4 categories × 4 months = 16 monthly rows → enough to train RF (MIN=10)
def _row(tid, date, direction, amount, narration, merchant):
    return f"{tid},{date},10:00,{direction},{amount},{narration},{merchant}\n"

_rows = []
cats = [
    ("supermarche carrefour", "Carrefour", 200, 20),
    ("TRANSPORT CAREEM", "Careem", 50, 8),
    ("loyer appartement", "Loyer", 3000, 5),
    ("pharmacie", "Pharmacie", 150, 6),
]
_idx = 1
for month in range(1, 5):       # Jan–Apr 2024
    for narration, merchant, base_amt, count in cats:
        for day in range(1, count + 1):
            date = f"2024-{month:02d}-{day:02d}"
            _rows.append(_row(f"TX{_idx:04d}", date, "Debit", base_amt + _idx % 10, narration, merchant))
            _idx += 1
    # One credit per month
    _rows.append(_row(f"TX{_idx:04d}", f"2024-{month:02d}-01", "Credit", 5000, "salaire", "Salaire"))
    _idx += 1

CSV = "transaction_id,transaction_date,transaction_time,direction,amount,narration,merchant_name\n" + "".join(_rows)


@pytest.fixture
def loaded_client(auth_client):
    f = SimpleUploadedFile('t.csv', CSV.encode(), content_type='text/csv')
    auth_client.post(reverse('upload_csv'), {'file': f}, format='multipart')
    return auth_client


@pytest.mark.django_db
class TestMLMetrics:
    def test_ml_metrics_requires_auth(self, client):
        from rest_framework.test import APIClient
        r = APIClient().get(reverse('ml_metrics'))
        assert r.status_code == 401

    def test_ml_metrics_returns_list(self, loaded_client):
        r = loaded_client.get(reverse('ml_metrics'))
        assert r.status_code == 200
        assert 'models' in r.data

    def test_rf_metrics_stored_after_upload(self, loaded_client):
        r = loaded_client.get(reverse('ml_metrics'))
        assert r.status_code == 200
        names = [m['model_name'] for m in r.data['models']]
        assert 'random_forest' in names

    def test_rf_metrics_have_required_keys(self, loaded_client):
        r = loaded_client.get(reverse('ml_metrics'))
        rf = next((m for m in r.data['models'] if m['model_name'] == 'random_forest'), None)
        assert rf is not None
        for key in ('mae', 'rmse', 'r2'):
            assert key in rf['metrics']

    def test_rf_r2_is_float(self, loaded_client):
        r = loaded_client.get(reverse('ml_metrics'))
        rf = next(m for m in r.data['models'] if m['model_name'] == 'random_forest')
        assert isinstance(rf['metrics']['r2'], float)


@pytest.mark.django_db
class TestFeatureImportance:
    def test_feature_importance_requires_auth(self, client):
        from rest_framework.test import APIClient
        r = APIClient().get(reverse('feature_importance'))
        assert r.status_code == 401

    def test_feature_importance_returns_list(self, loaded_client):
        r = loaded_client.get(reverse('feature_importance'))
        assert r.status_code == 200
        assert 'features' in r.data

    def test_feature_importance_has_6_features(self, loaded_client):
        r = loaded_client.get(reverse('feature_importance'))
        assert len(r.data['features']) == 6

    def test_feature_importance_sum_is_1(self, loaded_client):
        r = loaded_client.get(reverse('feature_importance'))
        total = sum(f['importance'] for f in r.data['features'])
        assert abs(total - 1.0) < 0.01

    def test_feature_importance_fields(self, loaded_client):
        r = loaded_client.get(reverse('feature_importance'))
        for f in r.data['features']:
            assert 'feature' in f
            assert 'importance' in f
            assert 'rank' in f
            assert 'importance_pct' in f


@pytest.mark.django_db
class TestAnomalyNewTypes:
    def test_anomaly_types_include_new_names(self, loaded_client):
        r = loaded_client.get(reverse('anomaly_list'))
        assert r.status_code == 200
        if r.data['count'] > 0:
            types = {a['anomaly_type'] for a in r.data['results']}
            valid = {
                'ml_isolation_forest', 'rule_high_amount', 'rule_odd_hour',
                'high_amount', 'odd_hour', 'category_spike', 'unusual_frequency',
            }
            assert types.issubset(valid)


@pytest.mark.django_db
class TestRecommendationReason:
    def test_recommendations_have_reason_field(self, loaded_client):
        r = loaded_client.get(reverse('recommendation_list'))
        assert r.status_code == 200
        for rec in r.data:
            assert 'reason' in rec
