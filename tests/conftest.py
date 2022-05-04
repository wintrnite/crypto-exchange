import os
from decimal import Decimal

import pytest

from app import urls
from app.constants import Operation, Settings
from app.db import (
    Base,
    Cryptocurrency,
    OperationsHistory,
    User,
    create_session,
    engine,
    init_db,
)


@pytest.fixture(autouse=True)
def _init_db():
    init_db(Base, engine)
    yield
    os.remove('app.db')


@pytest.fixture()
def client():
    test_client = urls.app.test_client()
    return test_client


@pytest.fixture()
def user_name():
    return 'keks'


@pytest.fixture()
def register_user(user_name):
    with create_session() as session:
        user = User(user_name=user_name, balance=Settings.balance.value)
        session.merge(user)


@pytest.fixture()
def buy_crypto_by_user(user_name, register_user):
    with create_session() as session:
        crypto = session.query(Cryptocurrency).first()
        user = session.query(User).filter(User.user_name == user_name).one()
        user.balance = str(
            Decimal(Settings.balance.value) - Decimal(crypto.buying_price)
        )
        session.merge(user)
        operation_history = OperationsHistory(
            user_name=user_name,
            operation=Operation.buy.value,
            crypto_name=crypto.crypto_name,
            count='1',
        )
        session.merge(operation_history)
