# beeteasea

BTC exchange platform "🐝☕🌊"


## How to run

To run platform execute `docker-compose -f docker-compose.yml -f docker-compose.dev.yml up`

Then API endpoints will be availiable at http://localhost:5000/api/

## API endpoints

### Create new user
Request:
```
POST /api/users

{
    "name": "username"
}
```

Response:
```
Status: 201

{
    "name": "username",
    "token": "user token"
}
```

Notes: use this token in further requests by adding it into `Authorization` header.
```Authorization: Bearer your_token```


### Create new wallet
Request:
```
POST /api/wallets
```

Response:
```
Status: 201

{
    "address": wallet_address,
    "balance": balance_in_satoshi,
    "usd_balance": balance_in_USA_dollars
}
```

### Get wallet balance
Request:
```
GET /api/wallets/:address
```

Response:
```
Status: 200

{
    "address": wallet_address,
    "balance": balance_in_satoshi,
    "usd_balance": balance_in_USA_dollars
}
```

### Get wallet transactions
Request:
```
GET /api/wallets/:address/transactions
```

Response:
```
Status: 200

{
    "transactions": [
        {
            "source": source_wallet_address,
            "destination": destination_wallet_address,
            "amount": transaction_amount_in_satoshi,
            "cost": platform_profit_in_satoshi,
            "timestamp": transaction_timestamp
        }
    ]
}
```

### Get user transactions
Request:
```
GET /api/transactions
```

Response:
```
Status: 200

{
    "transactions": [
        {
            "source": source_wallet_address,
            "destination": destination_wallet_address,
            "amount": transaction_amount_in_satoshi,
            "cost": platform_profit_in_satoshi,
            "timestamp": transaction_timestamp
        }
    ]
}
```

### Create new transaction
Request:
```
POST /api/transactions

{
    "source": source_wallet_address,
    "destination": destination_wallet_address,
    "amount": transaction_amount_in_satoshi
}
```

Response:
```
Status: 201

{
    "source": source_wallet_address,
    "destination": destination_wallet_address,
    "amount": transaction_amount_in_satoshi,
    "cost": platform_profit_in_satoshi,
    "timestamp": transaction_timestamp
}
```


### Get platform statistics
Request:
```
GET /api/statistics
```

Response:
```
Status: 200

{
    "transactions_amount": number_of_transactions,
    "platform_profit": platform_profit_in_satoshi
}
```

Notes: use admin token "melon" in this request by adding it into Authorization header. Authorization: Bearer melon
