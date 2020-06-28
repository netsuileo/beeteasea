from flask import Flask, jsonify
from flask_httpauth import HTTPTokenAuth
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config.update(
    DEBUG=True,
    SECRET_KEY='satoshi_HUoiFQzMcjNysgWz9HU5BQ_nakamoto',
    DATABASE_URI = 'postgresql://beeteesea:beeteesea@postgres/beeteesea'
)

db = SQLAlchemy(app)

auth = HTTPTokenAuth()
ADMIN_TOKEN = "melon"


@auth.verify_token
def verify_token(token):
    if token == ADMIN_TOKEN:
        return True
    # TODO: User authorization
    return False


@app.route('/api/users', methods=['POST'])
@auth.login_required
def create_user():
    # Create user
    # TODO
    return jsonify({'error': 'Not implemented'}), 501


@app.route('/api/wallets', methods=['POST'])
def create_wallet():
    # Create wallet
    # TODO
    return jsonify({'error': 'Not implemented'}), 501


@app.route('/api/wallets/:address', methods=['GET'])
def get_wallet():
    # TODO
    return jsonify({'error': 'Not implemented'}), 501


@app.route('/api/wallets/:address/transactions', methods=['GET'])
def get_wallet_transactions():
    # TODO
    return jsonify({'error': 'Not implemented'}), 501


@app.route('/api/transactions', methods=['GET'])
def get_user_transactions():
    # TODO
    return jsonify({'error': 'Not implemented'}), 501


@app.route('/api/transactions', methods=['POST'])
def create_transaction():
    # TODO
    return jsonify({'error': 'Not implemented'}), 501


@app.route('/api/statistics', methods=['GET'])
@auth.login_required
def statistics():
    # TODO: return real statistics
    return jsonify([])
