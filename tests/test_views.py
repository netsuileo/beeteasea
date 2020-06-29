import os
import tempfile

import pytest

from api import app as api
from .helpers import get_auth_headers


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
