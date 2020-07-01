from secrets import token_hex
from datetime import datetime
from flask_sqlalchemy import SQLAlchemy


db = SQLAlchemy()


ONE_BTC = 100_000_000  # in Satoshi


def generate_token():
    return token_hex(32)


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), index=True, nullable=False, unique=True)
    token = db.Column(db.String(64), index=True,
                      unique=True, default=generate_token)

    def __repr__(self):
        return f'<User {self.name} (token: {self.token})>'


class Wallet(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    private_key = db.Column(db.String(64), nullable=False)
    public_key = db.Column(db.String(130), nullable=False)
    address = db.Column(db.String(35), index=True, nullable=False, unique=True)
    balance = db.Column(db.BigInteger, nullable=False, default=ONE_BTC)

    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    user = db.relationship('User', backref=db.backref('wallets'))

    def __repr__(self):
        return f'<Wallet {self.address} (balance: {self.balance} satoshi)>'


class Transaction(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    source = db.Column(db.String(35), db.ForeignKey('wallet.address'),
                       nullable=False)
    destination = db.Column(db.String(35), db.ForeignKey('wallet.address'),
                            nullable=False)
    amount = db.Column(db.BigInteger, nullable=False)
    cost = db.Column(db.BigInteger, nullable=False, default=0)
    timestamp = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    def __repr__(self):
        return f'<Transaction {self.amount} (timestamp: {self.timestamp})>'
