from flask_marshmallow import Marshmallow
from marshmallow import fields as ma_fields
from marshmallow.validate import Range
from .exchange_rates import exchange_rate

ma = Marshmallow()
exchange_rates_generator = exchange_rate()


class UserSchema(ma.Schema):
    class Meta:
        fields = ("name", "token")

user_schema = UserSchema()
users_schema = UserSchema(many=True)


class CreateUserSchema(ma.Schema):
    name = ma_fields.String(required=True)

create_user_schema = CreateUserSchema()

class WalletSchema(ma.Schema):
    class Meta:
        fields = ("address", "balance", "usd_balance")

    usd_balance = ma_fields.Method("get_usd_balance")

    def get_usd_balance(self, obj):
        rate = next(exchange_rates_generator)
        return "{:.2f}".format(rate * obj.balance)

wallet_schema = WalletSchema()
wallets_schema = WalletSchema(many=True)


class TransactionSchema(ma.Schema):
    class Meta:
        fields = ("source", "destination", "amount", "timestamp")

transaction_schema = TransactionSchema()
transactions_schema = TransactionSchema(many=True)


class CreateTransactionSchema(ma.Schema):
    source = ma_fields.String(required=True)
    destination = ma_fields.String(required=True)
    amount = ma_fields.Integer(
        required=True,
        validate=[Range(min=1, error="Value must be greater than 0")])

create_transaction_schema = CreateTransactionSchema()
