import pytest


def test_register_success(client):
    resp = client.post('/api/v1/auth/register', json={
        'email': 'new@example.com',
        'password': 'Secure123',
        'full_name': 'New User',
    })
    assert resp.status_code == 201
    data = resp.get_json()
    assert 'token' in data
    assert data['user']['email'] == 'new@example.com'


def test_register_duplicate_email(client, test_user):
    resp = client.post('/api/v1/auth/register', json={
        'email': 'test@example.com',
        'password': 'Secure123',
        'full_name': 'Dup User',
    })
    assert resp.status_code == 409


def test_register_invalid_email(client):
    resp = client.post('/api/v1/auth/register', json={
        'email': 'not-an-email',
        'password': 'Secure123',
        'full_name': 'Test',
    })
    assert resp.status_code == 400
    assert 'error' in resp.get_json()


def test_register_weak_password(client):
    resp = client.post('/api/v1/auth/register', json={
        'email': 'weak@example.com',
        'password': 'short',
        'full_name': 'Weak',
    })
    assert resp.status_code == 400


def test_login_success(client, test_user):
    resp = client.post('/api/v1/auth/login', json={
        'email': 'test@example.com',
        'password': 'Password1',
    })
    assert resp.status_code == 200
    assert 'token' in resp.get_json()


def test_login_wrong_password(client, test_user):
    resp = client.post('/api/v1/auth/login', json={
        'email': 'test@example.com',
        'password': 'WrongPass1',
    })
    assert resp.status_code == 401


def test_login_unknown_email(client):
    resp = client.post('/api/v1/auth/login', json={
        'email': 'nobody@example.com',
        'password': 'Password1',
    })
    assert resp.status_code == 401


def test_protected_route_without_token(client):
    resp = client.get('/api/v1/tasks')
    assert resp.status_code == 401
