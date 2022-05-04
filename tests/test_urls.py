from decimal import Decimal

import pytest
from requests import codes

from app.constants import AddNewCryptoFormArgs, OperationFormArgs, Settings, QueryParams
from app.db import Cryptocurrency, OperationsHistory, create_session


@pytest.mark.parametrize('url', ['/'])
def test_base_route(url: str, client):
    response = client.get(url)
    assert response.status_code == codes['OK']
    assert response.json


def test_register_user(client, user_name):
    response = client.post('/register', data={'user_name': user_name})
    assert response.status_code == codes['OK']
    assert response.json['registered_user'] == user_name


@pytest.mark.usefixtures('register_user')
def test_get_balance(client, user_name):
    response = client.get(f'/{user_name}/balance')
    assert response.status_code == codes['OK']
    assert response.json['balance'] == Settings.balance.value


@pytest.mark.usefixtures('register_user')
def test_get_portfolio(client, user_name):
    response = client.get(f'/{user_name}/portfolio')
    assert response.status_code == codes['OK']
    assert response.json


@pytest.mark.usefixtures('register_user')
def test_buy_crypto(client, user_name):
    with create_session() as session:
        crypto = session.query(Cryptocurrency).first()
        crypto_name = crypto.crypto_name
        price = crypto.buying_price
    response = client.post(
        f'/{user_name}/buy',
        data={
            OperationFormArgs.crypto_name.value: crypto_name,
            OperationFormArgs.count.value: 1,
            OperationFormArgs.price.value: price,
        },
    )
    assert response.status_code == codes['OK']
    assert client.get(f'/{user_name}/balance').json['balance'] == str(
        Decimal(Settings.balance.value) - Decimal(price)
    )


@pytest.mark.usefixtures('register_user')
def test_buy_crypto_with_incorrect_price(client, user_name):
    with create_session() as session:
        crypto = session.query(Cryptocurrency).first()
        crypto_name = crypto.crypto_name
        price = str(Decimal(crypto.buying_price) - 1)
    response = client.post(
        f'/{user_name}/buy',
        data={
            OperationFormArgs.crypto_name.value: crypto_name,
            OperationFormArgs.count.value: 1,
            OperationFormArgs.price.value: price,
        },
    )
    assert response.status_code == codes['bad_request']


@pytest.mark.usefixtures('buy_crypto_by_user')
def test_sell_crypto(client):
    with create_session() as session:
        operation_history = session.query(OperationsHistory).first()
        name = operation_history.user_name
        crypto_name = operation_history.crypto_name
        count = operation_history.count
        price = (
            session.query(Cryptocurrency)
            .filter(Cryptocurrency.crypto_name == crypto_name)
            .one()
            .selling_price
        )
    balance_before_sell = Decimal(client.get(f'/{name}/balance').json['balance'])
    response = client.post(
        f'/{name}/sell',
        data={
            OperationFormArgs.crypto_name.value: crypto_name,
            OperationFormArgs.count.value: count,
            OperationFormArgs.price.value: price,
        },
    )
    balance_after_sell = Decimal(client.get(f'/{name}/balance').json['balance'])
    assert response.status_code == codes['OK']
    assert balance_after_sell > balance_before_sell


@pytest.mark.usefixtures('buy_crypto_by_user')
def test_sell_crypto_with_incorrect_price(client):
    with create_session() as session:
        operation_history = session.query(OperationsHistory).first()
        name = operation_history.user_name
        crypto_name = operation_history.crypto_name
        count = operation_history.count
        price = str(
            Decimal(
                session.query(Cryptocurrency)
                .filter(Cryptocurrency.crypto_name == crypto_name)
                .one()
                .selling_price
            )
            - 1
        )
        response = client.post(
            f'/{name}/sell',
            data={
                OperationFormArgs.crypto_name.value: crypto_name,
                OperationFormArgs.count.value: count,
                OperationFormArgs.price.value: price,
            },
        )
        assert response.status_code == codes['bad_request']


def test_add_new_crypto(client):
    with create_session() as session:
        cryptocurrencies_count_before_add = len(session.query(Cryptocurrency).all())
    response = client.post(
        '/add',
        data={
            AddNewCryptoFormArgs.crypto_name.value: 'shrek',
            AddNewCryptoFormArgs.buy_price.value: '100000',
            AddNewCryptoFormArgs.sell_price.value: '10202',
        },
    )
    with create_session() as session:
        cryptocurrencies_count_after_add = len(session.query(Cryptocurrency).all())
    assert response.status_code == codes['OK']
    assert cryptocurrencies_count_after_add - 1 == cryptocurrencies_count_before_add


@pytest.mark.usefixtures('buy_crypto_by_user')
def test_show_history(client, user_name):
    limit, page = 10, 0
    response = client.get(
        f'/{user_name}/history?{QueryParams.limit.value}={limit}&{QueryParams.page.value}={page}'
    )
    assert response.status_code == codes['OK']
    assert response.json
