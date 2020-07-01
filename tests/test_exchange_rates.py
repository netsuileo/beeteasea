from decimal import Decimal
from datetime import datetime
from unittest.mock import patch
from api import exchange_rates


@patch('api.exchange_rates.urlopen')
def test_exchange_rates_generator(mock_urlopen):
    mock_urlopen.return_value.__enter__.return_value.read = lambda: b'''{
        "price": "10000.00",
        "currency": "USD"
    }'''

    exchange_rate_generator = exchange_rates.exchange_rate()
    assert next(exchange_rate_generator) == Decimal(10000) / 100_000_000

    mock_urlopen.return_value.__enter__.return_value.read = lambda: b'''{
        "price": "5000.00",
        "currency": "USD"
    }'''
    # Does not ask for new value if TIMEOUT is not passed yet
    assert next(exchange_rate_generator) == Decimal(10000) / 100_000_000

    # Asks for new value if TIMEOUT is passed
    with patch('api.exchange_rates.datetime') as m_dt:
        m_dt.now.return_value = datetime.now() + exchange_rates.TIMEOUT
        assert next(exchange_rate_generator) == Decimal(5000) / 100_000_000
