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

    db.create_all()

    yield client

    ctx.pop()
