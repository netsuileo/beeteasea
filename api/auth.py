from sqlalchemy.orm.exc import NoResultFound
from flask_httpauth import HTTPTokenAuth
from .constants import ADMIN_USERNAME, ADMIN_TOKEN
from .models import User


auth = HTTPTokenAuth()


@auth.get_user_roles
def get_user_roles(username):
    if username == ADMIN_USERNAME:
        return 'admin'
    return 'user'


@auth.verify_token
def verify_token(token):
    if token == ADMIN_TOKEN:
        return ADMIN_USERNAME
    try:
        return User.query.filter(User.token == token).one().name
    except NoResultFound:
        return None


def current_user():
    return User.query.filter(User.name == auth.current_user()).one()
