import pytest
from unittest.mock import patch
from api import app as api
from .helpers import (
    get_auth_headers,
    get_random_string,
    create_user,
    create_wallet
)

@pytest.fixture
def client():
    api.app.config['TESTING'] = True
    api.app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite://'
    api.db.create_all()
    with api.app.test_client() as client:
        yield client


def test_create_user(client):
    URL = '/api/users'

    # Test wrong json
    # TODO: add json validation first
    # resp = client.post(URL, json={'some_invalid': 'field'})
    # assert resp.status_code == 400

    # Test create new user
    resp = client.post(URL, json={'name': 'satoshi'})
    assert resp.status_code == 201
    assert resp.json['name'] == 'satoshi'
    assert resp.json['token'] is not None


@patch('api.app.exchange_rates_generator')
def test_create_wallet(exchange_rate_mock, client):
    URL = '/api/wallets'
    exchange_rate_mock.__next__.return_value = 5000 / 100_000_000

    # TODO: Move create user into separate helper or fixture
    user = create_user()

    # Test wallet created successfully
    # TODO: mock exchange_rates_generator
    resp = client.post(URL, headers=get_auth_headers(user.token))
    assert resp.status_code == 201
    assert resp.json['balance'] == api.ONE_BTC
    assert resp.json['usd_balance'] == "5000.00"
    assert resp.json['address'] is not None

    # Test cannot create more than 10 wallets
    for _ in range(9):
        client.post(URL, headers=get_auth_headers(user.token))
    resp = client.post(URL, headers=get_auth_headers(user.token))
    assert resp.status_code == 400


@patch('api.app.exchange_rates_generator')
def test_get_wallet(exchange_rate_mock, client):
    exchange_rate_mock.__next__.return_value = 5000 / 100_000_000
    user = create_user()
    wallet = create_wallet(user)

    # Test get existing wallet
    URL = f'/api/wallets/{wallet.address}'
    resp = client.get(URL, headers=get_auth_headers(user.token))
    assert resp.status_code == 200
    assert resp.json['address'] == wallet.address
    assert resp.json['balance'] == api.ONE_BTC
    assert resp.json['usd_balance'] == "5000.00"

    # Test get non existing wallet
    URL = f'/api/wallets/{get_random_string(40)}'
    resp = client.get(URL, headers=get_auth_headers(user.token))
    assert resp.status_code == 404


def test_statistics(client):
    URL = '/api/statistics'
    # Test authentication failed
    resp = client.get(URL)
    assert resp.status_code == 401

    # Test authentication succeed
    resp = client.get(URL, headers=get_auth_headers(api.ADMIN_TOKEN))
    assert resp.status_code == 200
    
    # Test data is correct
    # TODO: Add some data into database
    # TODO: Test statistics contains this data
    assert resp.json == []
