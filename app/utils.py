import random
import time
from collections import defaultdict
from datetime import datetime
from decimal import Decimal

from app.constants import Operation, Settings
from app.db import Cryptocurrency, OperationsHistory, create_session


def get_portfolio_with_filters(*filters: bool) -> dict[str, Decimal]:
    crypto_count: defaultdict[str, Decimal] = defaultdict(Decimal)
    with create_session() as session:
        table = session.query(OperationsHistory).filter(*filters).all()
        for row in table:
            if row.operation == Operation.buy.value:
                crypto_count[row.crypto_name] += Decimal(row.count)
            elif row.operation == Operation.sell.value:
                crypto_count[row.crypto_name] -= Decimal(row.count)
    return {
        crypto_name: count for (crypto_name, count) in crypto_count.items() if count > 0
    }


def change_currencies_rates() -> None:  # pragma: no cover (как это протестировать?)
    while True:
        time.sleep(Settings.exchange_rates_update.value)
        with create_session() as session:
            cryptocurrencies = session.query(Cryptocurrency).all()
            for cryptocurrency in cryptocurrencies:
                sell_multiplier = Decimal(random.uniform(0.9, 1.1))
                buy_multiplier = Decimal(random.uniform(0.9, 1.1))
                cryptocurrency.selling_price = str(
                    round(
                        Decimal(cryptocurrency.selling_price) * sell_multiplier,
                        Settings.decimal_place.value,
                    )
                )
                cryptocurrency.buying_price = str(
                    round(
                        Decimal(cryptocurrency.buying_price) * buy_multiplier,
                        Settings.decimal_place.value,
                    )
                )
                cryptocurrency.modification_date = datetime.now()
