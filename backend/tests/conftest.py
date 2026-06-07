import pytest

from app import create_app
from app.config import TestConfig
from app.utils.db import db as _db
from app.models.user import User
from app.utils.auth import hash_password


@pytest.fixture(scope='session')
def app():
    app = create_app(TestConfig)
    with app.app_context():
        _db.create_all()
        yield app
        _db.drop_all()


@pytest.fixture(scope='function')
def db(app):
    with app.app_context():
        yield _db
        _db.session.rollback()


@pytest.fixture
def client(app):
    return app.test_client()


@pytest.fixture
def test_user(db):
    user = User(
        email='test@example.com',
        password_hash=hash_password('Password1'),
        full_name='Test User',
        role='member',
    )
    db.session.add(user)
    db.session.commit()
    return user


@pytest.fixture
def auth_headers(client, test_user):
    resp = client.post('/api/v1/auth/login', json={
        'email': 'test@example.com',
        'password': 'Password1',
    })
    token = resp.get_json()['token']
    return {'Authorization': f'Bearer {token}'}
