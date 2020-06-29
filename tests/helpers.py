import random
import string
from api import app as api


def get_random_string(length):
    letters = string.ascii_lowercase
    return ''.join(random.choice(letters) for i in range(length))


def get_auth_headers(token):
    return {
        'Authorization': f'Bearer {token}'
    }


def create_user():
    user = api.User(name=get_random_string(20))
    api.db.session.add(user)
    api.db.session.commit()
    return user


def create_wallet(user):
    wallet = api.Wallet(user=user, address=get_random_string(40),
                        private_key=get_random_string(64),
                        public_key=get_random_string(130))
    api.db.session.add(wallet)
    api.db.session.commit()
    return wallet
