from functools import wraps
from flask import Blueprint, jsonify, request
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm.exc import NoResultFound
from marshmallow.exceptions import ValidationError
from bitcoin import random_key, privtopub, pubtoaddr

from .auth import auth, current_user
from .models import db, User, Wallet, Transaction
from .schemas import (
    create_user_schema,
    create_transaction_schema,
    user_schema,
    wallet_schema,
    transaction_schema
)


views = Blueprint('main', __name__)


def validate_json(schema):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            try:
                schema.load(request.get_json())
            except ValidationError as ex:
                return jsonify(ex.messages), 400
            return func(*args, **kwargs)
        return wrapper
    return decorator


@views.route('/api/users', methods=['POST'])
@validate_json(create_user_schema)
def create_user():
    """ Create new user """
    username = request.get_json()['name']
    try:
        new_user = User(name=username)
        db.session.add(new_user)
        db.session.commit()
    except IntegrityError:
        return jsonify({'error': f'User named {username} already exists'}), 400
    return user_schema.dump(new_user), 201


@views.route('/api/wallets', methods=['POST'])
@auth.login_required(role='user')
def create_wallet():
    """ Create new wallet for user """
    # Create wallet
    user = current_user()
    if len(user.wallets) >= 10:
        return jsonify({'error': 'User already has 10 wallets'}), 400

    private_key = random_key()
    public_key = privtopub(private_key)
    address = pubtoaddr(public_key)

    new_wallet = Wallet(
        user=user, private_key=private_key,
        public_key=public_key, address=address)
    db.session.add(new_wallet)
    db.session.commit()
    return wallet_schema.dump(new_wallet), 201


@views.route('/api/wallets/<address>', methods=['GET'])
@auth.login_required(role='user')
def get_wallet(address):
    """ Get info about user wallet """
    user = current_user()
    try:
        wallet = Wallet.query.filter(
            Wallet.user == user, Wallet.address == address
        ).one()
        return wallet_schema.dump(wallet), 200
    except NoResultFound:
        return jsonify({'error': 'Not found'}), 404


@views.route('/api/wallets/:address/transactions', methods=['GET'])
@auth.login_required(role='user')
def get_wallet_transactions():
    # TODO
    return jsonify({'error': 'Not implemented'}), 501


@views.route('/api/transactions', methods=['GET'])
@auth.login_required(role='user')
def get_user_transactions():
    # TODO
    return jsonify({'error': 'Not implemented'}), 501


@views.route('/api/transactions', methods=['POST'])
@auth.login_required(role='user')
@validate_json(create_transaction_schema)
def create_transaction():
    json = request.get_json()

    source = Wallet.query.filter(
        Wallet.address == json['source']).one()
    destination = Wallet.query.filter(
        Wallet.address == json['destination']).one()
    amount = json['amount']

    new_transaction = Transaction(
        source=source.address,
        destination=destination.address,
        amount=amount)

    if source.balance - amount < 0:
        return jsonify({'error': 'Source balance is insufficient.'}), 400

    source.balance -= amount
    destination.balance += amount
    db.session.add(new_transaction)
    db.session.add(source)
    db.session.add(destination)
    db.session.commit()
    return transaction_schema.dump(new_transaction), 201


@views.route('/api/statistics', methods=['GET'])
@auth.login_required(role='admin')
def statistics():
    # TODO: return real statistics
    return jsonify([])
