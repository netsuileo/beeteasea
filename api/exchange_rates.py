import json
from urllib.request import Request, urlopen
from datetime import datetime, timedelta


TIMEOUT = timedelta(minutes=5)


def exchange_rate():
    exchange_rate = None
    timestamp = datetime(1970, 1, 1)
    while True:
        if datetime.now() > timestamp + TIMEOUT:
            exchange_rate = fetch_exchange_rate()
            timestamp = datetime.now()
        yield exchange_rate


def fetch_exchange_rate():
    request = Request('https://paxful.com/api/currency/btc')
    request.add_header('Content-Type', 'text/plain')
    request.add_header('Accept', 'application/json')
    with urlopen(request) as response:
        text = response.read()
        return float(json.loads(text, encoding='utf-8')['price']) / 100_000_000
