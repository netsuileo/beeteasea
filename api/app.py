# TODO: split into separate files

from secrets import token_hex
from flask import Flask, jsonify, request
from flask_httpauth import HTTPTokenAuth
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm.exc import NoResultFound
from flask_migrate import Migrate
from flask_marshmallow import Marshmallow
import bitcoin


# Application
# ----------------------------------------------------------------
app = Flask(__name__)
app.config.update(
    DEBUG=True,
    SECRET_KEY='satoshi_HUoiFQzMcjNysgWz9HU5BQ_nakamoto',
    SQLALCHEMY_DATABASE_URI='postgresql://beeteesea:beeteesea@postgres/beeteesea'
)
# ----------------------------------------------------------------


# Database
# ----------------------------------------------------------------
db = SQLAlchemy(app)
migrate = Migrate(app, db)
# ----------------------------------------------------------------


# Models
# ----------------------------------------------------------------
ONE_BTC = 100_000_000  # in Satoshi

def generate_token():
    return token_hex(32)


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), nullable=False, unique=True)
    token = db.Column(db.String(64), index=True,
                      unique=True, default=generate_token)

    def __repr__(self):
        return f'<User {self.name} (token: {self.token})>'


class Wallet(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    private_key = db.Column(db.String(64), nullable=False)
    public_key = db.Column(db.String(130), nullable=False)
    address = db.Column(db.String(35), nullable=False, unique=True)
    balance = db.Column(db.BigInteger, nullable=False, default=ONE_BTC)

    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    user = db.relationship('User', backref=db.backref('wallets'))

    def __repr__(self):
        return f'<Wallet {self.address} (balance: {self.balance} satoshi)>'
# ----------------------------------------------------------------


# Auth
# ----------------------------------------------------------------
auth = HTTPTokenAuth()
ADMIN_USERNAME = "admin"
ADMIN_TOKEN = "melon"


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
# ----------------------------------------------------------------


# Schemas
# ----------------------------------------------------------------
ma = Marshmallow(app)

class UserSchema(ma.Schema):
    class Meta:
        fields = ("name", "token")

user_schema = UserSchema()
users_schema = UserSchema(many=True)


class WalletSchema(ma.Schema):
    class Meta:
        fields = ("address", "balance")

wallet_schema = WalletSchema()
wallets_schema = WalletSchema(many=True)
# ----------------------------------------------------------------


# Views
# ----------------------------------------------------------------
@app.route('/api/users', methods=['POST'])
def create_user():
    """ Create new user """
    # TODO: validate json before processing
    username = request.get_json()['name']
    try:
        new_user = User(name=username)
        db.session.add(new_user)
        db.session.commit()
    except IntegrityError:
        return jsonify({'error': f'User named {username} already exists'}), 400
    return user_schema.dump(new_user), 201


@app.route('/api/wallets', methods=['POST'])
@auth.login_required(role='user')
def create_wallet():
    """ Create new wallet for user """
    # Create wallet
    user = current_user()
    if len(user.wallets) >= 10:
        return jsonify({'error': 'User already has 10 wallets'}), 400

    private_key = bitcoin.random_key()
    public_key = bitcoin.privtopub(private_key)
    address = bitcoin.pubtoaddr(public_key)

    new_wallet = Wallet(
        user=user, private_key=private_key,
        public_key=public_key, address=address)
    db.session.add(new_wallet)
    db.session.commit()
    return wallet_schema.dump(new_wallet), 201


@app.route('/api/wallets/<address>', methods=['GET'])
@auth.login_required(role='user')
def get_wallet(address):
    user = current_user()
    try:
        wallet = Wallet.query.filter(
            Wallet.user == user, Wallet.address == address
        ).one()
        return wallet_schema.dump(wallet), 200
    except NoResultFound:
        return jsonify({'error': 'Not found'}), 404


@app.route('/api/wallets/:address/transactions', methods=['GET'])
@auth.login_required(role='user')
def get_wallet_transactions():
    # TODO
    return jsonify({'error': 'Not implemented'}), 501


@app.route('/api/transactions', methods=['GET'])
@auth.login_required(role='user')
def get_user_transactions():
    # TODO
    return jsonify({'error': 'Not implemented'}), 501


@app.route('/api/transactions', methods=['POST'])
@auth.login_required(role='user')
def create_transaction():
    # TODO
    return jsonify({'error': 'Not implemented'}), 501


@app.route('/api/statistics', methods=['GET'])
@auth.login_required(role='admin')
def statistics():
    # TODO: return real statistics
    return jsonify([])
# ----------------------------------------------------------------
