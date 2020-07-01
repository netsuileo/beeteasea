from unittest.mock import patch
from api.constants import ADMIN_TOKEN, ONE_BTC
from tests.helpers import (
    get_auth_headers,
    get_random_string,
    create_user,
    create_wallet,
    create_transaction
)


def test_create_user(client):
    URL = '/api/users'

    # Test wrong json
    resp = client.post(URL, json={'some_invalid': 'field'})
    assert resp.status_code == 400

    # Test create new user
    resp = client.post(URL, json={'name': 'satoshi'})
    assert resp.status_code == 201
    assert resp.json['name'] == 'satoshi'
    assert resp.json['token'] is not None


@patch('api.exchange_rates.exchange_rates_generator')
def test_create_wallet(exchange_rate_mock, client):
    URL = '/api/wallets'
    exchange_rate_mock.__next__.return_value = 5000 / 100_000_000
    user = create_user()

    # Test wallet created successfully
    resp = client.post(URL, headers=get_auth_headers(user.token))
    assert resp.status_code == 201
    assert resp.json['balance'] == ONE_BTC
    assert resp.json['usd_balance'] == "5000.00"
    assert resp.json['address'] is not None

    # Test cannot create more than 10 wallets
    for _ in range(9):
        client.post(URL, headers=get_auth_headers(user.token))
    resp = client.post(URL, headers=get_auth_headers(user.token))
    assert resp.status_code == 400


@patch('api.exchange_rates.exchange_rates_generator')
def test_get_wallet(exchange_rate_mock, client):
    exchange_rate_mock.__next__.return_value = 5000 / 100_000_000
    user = create_user()
    wallet = create_wallet(user)

    # Test get existing wallet
    URL = f'/api/wallets/{wallet.address}'
    resp = client.get(URL, headers=get_auth_headers(user.token))
    assert resp.status_code == 200
    assert resp.json['address'] == wallet.address
    assert resp.json['balance'] == ONE_BTC
    assert resp.json['usd_balance'] == "5000.00"

    # Test get non existing wallet
    URL = f'/api/wallets/{get_random_string(40)}'
    resp = client.get(URL, headers=get_auth_headers(user.token))
    assert resp.status_code == 404


def test_create_transaction(client):
    user = create_user()
    source_wallet = create_wallet(user)
    destination_wallet = create_wallet(user)

    other_user_wallet = create_wallet(create_user())

    URL = '/api/transactions'
    resp = client.post(URL, headers=get_auth_headers(user.token), json=dict(
        source=source_wallet.address,
        destination=destination_wallet.address,
        amount=1000
    ))
    assert resp.status_code == 201
    assert resp.json['source'] == source_wallet.address
    assert resp.json['destination'] == destination_wallet.address
    assert resp.json['amount'] == 1000
    assert resp.json['cost'] == 0
    assert resp.json['timestamp'] is not None

    resp = client.post(URL, headers=get_auth_headers(user.token), json=dict(
        source=source_wallet.address,
        destination=other_user_wallet.address,
        amount=2000
    ))
    assert resp.status_code == 201
    assert resp.json['source'] == source_wallet.address
    assert resp.json['destination'] == other_user_wallet.address
    assert resp.json['amount'] == 2000
    assert resp.json['cost'] == 30
    assert resp.json['timestamp'] is not None


def test_get_wallet_transactions(client):
    user_1 = create_user()
    user_2 = create_user()
    wallet_1 = create_wallet(user_1)
    wallet_2 = create_wallet(user_2)

    create_transaction(wallet_1, wallet_2, 1000)
    create_transaction(wallet_2, wallet_1, 2000)

    URL_1 = f'/api/wallets/{wallet_1.address}/transactions'
    resp_1 = client.get(URL_1, headers=get_auth_headers(user_1.token))
    assert resp_1.status_code == 200
    transactions_1 = resp_1.json['transactions']
    assert transactions_1[0]['source'] == wallet_1.address
    assert transactions_1[0]['destination'] == wallet_2.address
    assert transactions_1[0]['amount'] == 1000
    assert transactions_1[1]['source'] == wallet_2.address
    assert transactions_1[1]['destination'] == wallet_1.address
    assert transactions_1[1]['amount'] == 2000

    URL_2 = f'/api/wallets/{wallet_2.address}/transactions'
    resp_2 = client.get(URL_2, headers=get_auth_headers(user_2.token))
    assert resp_1.status_code == 200
    transactions_2 = resp_2.json['transactions']
    for t_1, t_2 in zip(transactions_1, transactions_2):
        assert t_1 == t_2


def test_get_user_transactions(client):
    user_1 = create_user()
    user_2 = create_user()
    wallet_1 = create_wallet(user_1)
    wallet_2 = create_wallet(user_2)
    wallet_3 = create_wallet(user_2)

    create_transaction(wallet_1, wallet_2, 1000)
    create_transaction(wallet_2, wallet_1, 2000)
    create_transaction(wallet_2, wallet_3, 3000)
    create_transaction(wallet_3, wallet_1, 4000)

    URL = '/api/transactions'
    resp_1 = client.get(URL, headers=get_auth_headers(user_1.token))
    assert resp_1.status_code == 200

    transactions_1 = resp_1.json['transactions']

    assert transactions_1[0]['source'] == wallet_1.address
    assert transactions_1[0]['destination'] == wallet_2.address
    assert transactions_1[0]['amount'] == 1000

    assert transactions_1[1]['source'] == wallet_2.address
    assert transactions_1[1]['destination'] == wallet_1.address
    assert transactions_1[1]['amount'] == 2000

    assert transactions_1[2]['source'] == wallet_3.address
    assert transactions_1[2]['destination'] == wallet_1.address
    assert transactions_1[2]['amount'] == 4000

    resp_2 = client.get(URL, headers=get_auth_headers(user_2.token))
    assert resp_2.status_code == 200

    transactions_2 = resp_2.json['transactions']
    assert transactions_2[0]['source'] == wallet_1.address
    assert transactions_2[0]['destination'] == wallet_2.address
    assert transactions_2[0]['amount'] == 1000

    assert transactions_2[1]['source'] == wallet_2.address
    assert transactions_2[1]['destination'] == wallet_1.address
    assert transactions_2[1]['amount'] == 2000

    assert transactions_2[2]['source'] == wallet_2.address
    assert transactions_2[2]['destination'] == wallet_3.address
    assert transactions_2[2]['amount'] == 3000

    assert transactions_2[3]['source'] == wallet_3.address
    assert transactions_2[3]['destination'] == wallet_1.address
    assert transactions_2[3]['amount'] == 4000


def test_statistics(client):
    URL = '/api/statistics'
    # Test authentication failed
    resp = client.get(URL)
    assert resp.status_code == 401

    # Test authentication succeed and data is correct
    user_1 = create_user()
    user_2 = create_user()
    wallet_1 = create_wallet(user_1)
    wallet_2 = create_wallet(user_2)
    wallet_3 = create_wallet(user_2)

    create_transaction_via_api(client, user_1, wallet_1, wallet_2, 1000)
    create_transaction_via_api(client, user_2, wallet_2, wallet_1, 2000)
    create_transaction_via_api(client, user_2, wallet_2, wallet_3, 3000)
    create_transaction_via_api(client, user_2, wallet_3, wallet_1, 4000)

    resp = client.get(URL, headers=get_auth_headers(ADMIN_TOKEN))
    assert resp.status_code == 200

    assert resp.json == {
        'transactions_amount': 4,
        'platform_profit': 105
    }


def create_transaction_via_api(client, user, source, destination, amount):
    URL = '/api/transactions'
    client.post(URL, headers=get_auth_headers(user.token), json=dict(
        source=source.address,
        destination=destination.address,
        amount=amount
    ))
