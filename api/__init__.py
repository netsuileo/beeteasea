from flask import Flask
from flask_migrate import Migrate
from .models import db
from .schemas import ma
from .views import views

CONFIG = dict(
    DEBUG=True,
    SECRET_KEY='satoshi_HUoiFQzMcjNysgWz9HU5BQ_nakamoto',
    SQLALCHEMY_DATABASE_URI='postgresql://beeteesea:beeteesea@postgres/beeteesea'  # noqa E501
)


def create_app():
    app = Flask(__name__)
    app.config.update(**CONFIG)
    with app.app_context():
        db.init_app(app)
        Migrate(app, db)
        ma.init_app(app)
        app.register_blueprint(views)
    return app
