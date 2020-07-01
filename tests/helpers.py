import random
import string
from api.models import db, User, Wallet, Transaction


def get_random_string(length):
    letters = string.ascii_lowercase
    return ''.join(random.choice(letters) for _ in range(length))


def get_auth_headers(token):
    return {
        'Authorization': f'Bearer {token}'
    }


def create_user():
    user = User(name=get_random_string(20))
    db.session.add(user)
    db.session.commit()
    return user


def create_wallet(user):
    wallet = Wallet(user=user, address=get_random_string(40),
                    private_key=get_random_string(64),
                    public_key=get_random_string(130))
    db.session.add(wallet)
    db.session.commit()
    return wallet


def create_transaction(source, destination, amount):
    transaction = Transaction(
        source=source.address, destination=destination.address, amount=amount)
    db.session.add(transaction)
    db.session.commit()
    return transaction
