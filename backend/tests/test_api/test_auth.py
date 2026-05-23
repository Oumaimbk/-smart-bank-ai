import pytest
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework.test import APIClient

User = get_user_model()


@pytest.fixture
def client():
    return APIClient()


@pytest.mark.django_db
def test_register_creates_user(client):
    url = reverse('register')
    payload = {
        'username': 'newuser',
        'email': 'new@example.com',
        'password': 'StrongPass123!',
        'password2': 'StrongPass123!',
    }
    response = client.post(url, payload, format='json')
    assert response.status_code == 201
    assert User.objects.filter(email='new@example.com').exists()


@pytest.mark.django_db
def test_register_rejects_mismatched_passwords(client):
    url = reverse('register')
    payload = {
        'username': 'user2',
        'email': 'user2@example.com',
        'password': 'StrongPass123!',
        'password2': 'WrongPass456!',
    }
    response = client.post(url, payload, format='json')
    assert response.status_code == 400


@pytest.mark.django_db
def test_login_returns_tokens(client, user):
    url = reverse('login')
    response = client.post(
        url,
        {'email': 'test@example.com', 'password': 'TestPass123!'},
        format='json',
    )
    assert response.status_code == 200
    assert 'access' in response.data
    assert 'refresh' in response.data
    assert 'user' in response.data


@pytest.mark.django_db
def test_me_requires_auth(client):
    url = reverse('me')
    response = client.get(url)
    assert response.status_code == 401


@pytest.mark.django_db
def test_me_returns_user_data(auth_client):
    url = reverse('me')
    response = auth_client.get(url)
    assert response.status_code == 200
    assert response.data['email'] == 'test@example.com'
