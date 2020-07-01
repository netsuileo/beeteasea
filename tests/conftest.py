import pytest
from api import create_app, CONFIG
from api.models import db


@pytest.fixture(scope='module')
def client():
    CONFIG['TESTING'] = True
    CONFIG['SQLALCHEMY_DATABASE_URI'] = 'sqlite://'
    app = create_app()

    client = app.test_client()

    ctx = app.app_context()
    ctx.push()

    yield client

    ctx.pop()


@pytest.fixture(autouse=True)
def init_database(client):
    db.create_all()
    yield
    db.drop_all()
