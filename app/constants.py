from enum import Enum


class Files(Enum):
    logs = 'app.log'
    db = 'app.db'


class QueryParams(Enum):
    limit = 'limit'
    page = 'page'


class FormArgs(Enum):
    crypto_name = 'crypto_name'
    count = 'count'
    user_name = 'user_name'


class OperationFormArgs(Enum):
    price = 'price'
    crypto_name = 'crypto_name'
    count = 'count'


class AddNewCryptoFormArgs(Enum):
    buy_price = 'buy_price'
    sell_price = 'sell_price'
    crypto_name = 'crypto_name'


class Operation(Enum):
    buy = 'buy'
    sell = 'sell'


class Settings(Enum):
    balance = '5000'
    decimal_place = 4
    exchange_rates_update = 10


class ErrorMessage(Enum):
    not_enough_money = 'Not enough money'
    price_changed = 'Price have changed, operation aborted'
    not_enough_count = 'Insufficient exchange, operation aborted'
    empty_input = 'Empty forms/args'
