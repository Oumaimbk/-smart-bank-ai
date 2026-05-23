import pytest
from django.core.files.uploadedfile import SimpleUploadedFile
from django.urls import reverse


CSV_HEADER = "transaction_id,customer_id,transaction_date,transaction_time,account_type,payment_method,direction,amount,balance_after,narration,merchant_name,merchant_city,merchant_country\n"
CSV_ROWS = (
    "TX0001,CUST01,2024-01-01,09:00,Courant,Carte,Debit,500.00,9500.00,CARREFOUR MARJANE,Carrefour,Rabat,MA\n"
    "TX0002,CUST01,2024-01-02,10:00,Courant,Virement instantané,Credit,5000.00,14500.00,virement employeur,Salaire,Rabat,MA\n"
    "TX0003,CUST01,2024-01-03,11:00,Courant,Wallet,Debit,21.55,14478.45,TRANSPORT CAREEM,Careem,Rabat,MA\n"
    "TX0004,CUST01,2024-01-04,12:00,Courant,Carte,Debit,3000.00,11478.45,loyer appartement,Loyer,Rabat,MA\n"
    "TX0005,CUST01,2024-02-01,09:00,Courant,Carte,Debit,600.00,10878.45,CARREFOUR MARJANE,Carrefour,Rabat,MA\n"
    "TX0006,CUST01,2024-02-02,10:00,Courant,Virement instantané,Credit,5000.00,15878.45,virement employeur,Salaire,Rabat,MA\n"
    "TX0007,CUST01,2024-02-03,11:00,Courant,Wallet,Debit,25.00,15853.45,TRANSPORT CAREEM,Careem,Rabat,MA\n"
    "TX0008,CUST01,2024-02-04,12:00,Courant,Carte,Debit,3000.00,12853.45,loyer appartement,Loyer,Rabat,MA\n"
    "TX0009,CUST01,2024-03-01,02:30,Courant,Carte,Debit,50000.00,0.00,suspicious night purchase,Unknown,Rabat,MA\n"
    "TX0010,CUST01,2024-03-02,10:00,Courant,Virement instantané,Credit,5000.00,5000.00,virement employeur,Salaire,Rabat,MA\n"
)

def make_csv(rows=CSV_ROWS):
    content = (CSV_HEADER + rows).encode('utf-8')
    return SimpleUploadedFile('transactions.csv', content, content_type='text/csv')


@pytest.mark.django_db
class TestCSVUpload:
    def test_upload_requires_auth(self, client):
        from rest_framework.test import APIClient
        c = APIClient()
        response = c.post(reverse('upload_csv'), {}, format='multipart')
        assert response.status_code == 401

    def test_upload_creates_transactions(self, auth_client):
        f = make_csv()
        response = auth_client.post(
            reverse('upload_csv'),
            {'file': f},
            format='multipart',
        )
        assert response.status_code == 201
        data = response.data
        assert data['new_transactions'] == 10
        assert data['skipped_duplicates'] == 0
        assert 'batch_id' in data

    def test_upload_rejects_non_csv(self, auth_client):
        f = SimpleUploadedFile('data.txt', b'not a csv', content_type='text/plain')
        response = auth_client.post(
            reverse('upload_csv'),
            {'file': f},
            format='multipart',
        )
        assert response.status_code == 400

    def test_upload_skips_duplicates(self, auth_client):
        auth_client.post(reverse('upload_csv'), {'file': make_csv()}, format='multipart')
        response = auth_client.post(
            reverse('upload_csv'),
            {'file': make_csv()},
            format='multipart',
        )
        assert response.status_code == 201
        assert response.data['new_transactions'] == 0
        assert response.data['skipped_duplicates'] == 10

    def test_upload_detects_anomalies(self, auth_client):
        response = auth_client.post(
            reverse('upload_csv'),
            {'file': make_csv()},
            format='multipart',
        )
        assert response.status_code == 201
        assert response.data['anomalies_detected'] > 0

    def test_upload_missing_file(self, auth_client):
        response = auth_client.post(reverse('upload_csv'), {}, format='multipart')
        assert response.status_code == 400


@pytest.mark.django_db
class TestTransactionList:
    def _upload(self, auth_client):
        auth_client.post(reverse('upload_csv'), {'file': make_csv()}, format='multipart')

    def test_list_is_paginated(self, auth_client):
        self._upload(auth_client)
        response = auth_client.get(reverse('transaction_list'))
        assert response.status_code == 200
        assert 'count' in response.data
        assert 'results' in response.data
        assert response.data['count'] == 10

    def test_filter_by_direction(self, auth_client):
        self._upload(auth_client)
        response = auth_client.get(reverse('transaction_list'), {'direction': 'Credit'})
        assert response.status_code == 200
        assert all(t['direction'] == 'Credit' for t in response.data['results'])

    def test_search_by_narration(self, auth_client):
        self._upload(auth_client)
        response = auth_client.get(reverse('transaction_list'), {'search': 'careem'})
        assert response.status_code == 200
        assert response.data['count'] == 2

    def test_user_isolation(self, auth_client, db):
        from django.contrib.auth import get_user_model
        from rest_framework.test import APIClient
        from rest_framework_simplejwt.tokens import RefreshToken
        User = get_user_model()

        self._upload(auth_client)

        other = User.objects.create_user(username='other', email='other@test.com', password='pass')
        other_client = APIClient()
        other_client.credentials(HTTP_AUTHORIZATION=f'Bearer {RefreshToken.for_user(other).access_token}')

        response = other_client.get(reverse('transaction_list'))
        assert response.status_code == 200
        assert response.data['count'] == 0


@pytest.mark.django_db
class TestBatchDelete:
    def test_delete_batch_removes_transactions(self, auth_client):
        # Upload
        upload = auth_client.post(reverse('upload_csv'), {'file': make_csv()}, format='multipart')
        assert upload.status_code == 201
        batch_id = upload.data['batch_id']

        # Delete
        r = auth_client.delete(reverse('batch_delete', kwargs={'batch_id': batch_id}))
        assert r.status_code == 200
        assert r.data['deleted_transactions'] == 10
        assert 'message' in r.data

        # Transactions gone
        r2 = auth_client.get(reverse('transaction_list'))
        assert r2.data['count'] == 0

    def test_delete_batch_returns_404_second_time(self, auth_client):
        upload = auth_client.post(reverse('upload_csv'), {'file': make_csv()}, format='multipart')
        batch_id = upload.data['batch_id']
        auth_client.delete(reverse('batch_delete', kwargs={'batch_id': batch_id}))
        r = auth_client.delete(reverse('batch_delete', kwargs={'batch_id': batch_id}))
        assert r.status_code == 404

    def test_delete_batch_requires_auth(self, auth_client):
        from rest_framework.test import APIClient
        upload = auth_client.post(reverse('upload_csv'), {'file': make_csv()}, format='multipart')
        batch_id = upload.data['batch_id']
        r = APIClient().delete(reverse('batch_delete', kwargs={'batch_id': batch_id}))
        assert r.status_code == 401

    def test_delete_batch_user_isolation(self, auth_client, db):
        from django.contrib.auth import get_user_model
        from rest_framework.test import APIClient
        from rest_framework_simplejwt.tokens import RefreshToken
        User = get_user_model()

        upload = auth_client.post(reverse('upload_csv'), {'file': make_csv()}, format='multipart')
        batch_id = upload.data['batch_id']

        # Another user cannot delete this batch
        other = User.objects.create_user(username='other2', email='other2@test.com', password='pass')
        other_client = APIClient()
        other_client.credentials(HTTP_AUTHORIZATION=f'Bearer {RefreshToken.for_user(other).access_token}')
        r = other_client.delete(reverse('batch_delete', kwargs={'batch_id': batch_id}))
        assert r.status_code == 404  # not found for this user

    def test_can_reupload_after_delete(self, auth_client):
        upload1 = auth_client.post(reverse('upload_csv'), {'file': make_csv()}, format='multipart')
        batch_id = upload1.data['batch_id']
        auth_client.delete(reverse('batch_delete', kwargs={'batch_id': batch_id}))
        # Same file should import again (dedup IDs were removed)
        upload2 = auth_client.post(reverse('upload_csv'), {'file': make_csv()}, format='multipart')
        assert upload2.status_code == 201
        assert upload2.data['new_transactions'] == 10
