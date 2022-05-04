import logging
import threading
from datetime import datetime
from decimal import Decimal
from typing import Union

from flask import Flask, Response, jsonify, request
from sqlalchemy.exc import ArgumentError

from app.constants import (
    AddNewCryptoFormArgs,
    ErrorMessage,
    Files,
    FormArgs,
    Operation,
    OperationFormArgs,
    QueryParams,
    Settings,
)
from app.db import Base, Cryptocurrency, OperationsHistory, User, engine, init_db
from app.utils import (
    change_currencies_rates,
    create_session,
    get_portfolio_with_filters,
)

app = Flask(__name__)
logger = logging.getLogger(__name__)
logging.basicConfig(
    level=logging.INFO, filename=Files.logs.value, filemode='w', format='%(message)s'
)

init_db(Base, engine)


@app.route('/')
def show_exchange() -> tuple[Response, int]:
    with create_session() as session:
        currencies = session.query(Cryptocurrency).all()
        response = jsonify(currencies)
    return response, 200


@app.route('/register', methods=['POST'])
def reg_user() -> Union[tuple[Response, int], tuple[str, int]]:
    user_name = request.form.get(FormArgs.user_name.value)
    if user_name is None:
        return ErrorMessage.empty_input.value, 400
    with create_session() as session:
        user = User(user_name=user_name, balance=Settings.balance.value)
        session.merge(user)
    return jsonify(registered_user=user_name), 200


@app.route('/<string:user_name>/balance')
def get_balance(user_name: str) -> tuple[Response, int]:
    with create_session() as session:
        user_balance = (
            session.query(User).filter(User.user_name == user_name).one().balance
        )
    return jsonify(user_name=user_name, balance=user_balance), 200


@app.route('/<string:user_name>/buy', methods=['POST'])
def buy_cryptocurrency(user_name: str) -> Union[tuple[Response, int], tuple[str, int]]:
    buying_crypto_name = request.form.get(OperationFormArgs.crypto_name.value)
    buying_count = request.form.get(OperationFormArgs.count.value, type=Decimal)
    expected_exchange_rate_price = request.form.get(
        OperationFormArgs.price.value, type=Decimal
    )
    if (
        buying_crypto_name is None
        or buying_count is None
        or expected_exchange_rate_price is None
    ):
        return ErrorMessage.empty_input.value, 400
    try:
        with create_session() as session:
            crypto = (
                session.query(Cryptocurrency)
                .filter(Cryptocurrency.crypto_name == buying_crypto_name)
                .one()
            )
            user = session.query(User).filter(User.user_name == user_name).one()
            user_balance = Decimal(user.balance)
            total_price = Decimal(crypto.buying_price) * buying_count
            if total_price > user_balance:
                raise ArgumentError
            if expected_exchange_rate_price != Decimal(crypto.buying_price):
                raise TimeoutError
            user.balance = str(user_balance - total_price)
            current_operation_history = OperationsHistory(
                user_name=user.user_name,
                operation=Operation.buy.value,
                crypto_name=buying_crypto_name,
                count=str(buying_count),
            )
            session.merge(current_operation_history)
        return (
            jsonify(
                username=user_name,
                operation=Operation.buy.value,
                cryptocurrency=buying_crypto_name,
                count=buying_count,
            ),
            200,
        )
    except ArgumentError as e:
        logger.exception(e)
        return ErrorMessage.not_enough_money.value, 400
    except TimeoutError as e:
        logger.exception(e)
        return ErrorMessage.price_changed.value, 400


@app.route('/<string:user_name>/sell', methods=['POST'])
def sell_cryptocurrency(user_name: str) -> Union[tuple[Response, int], tuple[str, int]]:
    selling_count = request.form.get(OperationFormArgs.count.value, type=Decimal)
    selling_crypto_name = request.form.get(OperationFormArgs.crypto_name.value)
    expected_exchange_rate_price = request.form.get(
        OperationFormArgs.price.value, type=Decimal
    )
    if (
        selling_crypto_name is None
        or selling_count is None
        or expected_exchange_rate_price is None
    ):
        return ErrorMessage.empty_input.value, 400
    portfolio = get_portfolio_with_filters(
        OperationsHistory.user_name == user_name,
        OperationsHistory.crypto_name == selling_crypto_name,
    )
    if portfolio[selling_crypto_name] < selling_count:
        return ErrorMessage.not_enough_count.value, 400
    try:
        with create_session() as session:
            crypto = (
                session.query(Cryptocurrency)
                .filter(Cryptocurrency.crypto_name == selling_crypto_name)
                .one()
            )
            money = Decimal(crypto.selling_price) * selling_count
            user = session.query(User).filter(User.user_name == user_name).one()
            user.balance = str(Decimal(user.balance) + money)
            if Decimal(crypto.selling_price) != expected_exchange_rate_price:
                raise TimeoutError
            history = OperationsHistory(
                user_name=user_name,
                operation=Operation.sell.value,
                crypto_name=selling_crypto_name,
                count=str(selling_count),
            )
            session.merge(history)
    except TimeoutError as e:
        logger.exception(e)
        return ErrorMessage.price_changed.value, 400
    return (
        jsonify(
            username=user_name,
            operation=Operation.sell.value,
            cryptocurrency=selling_crypto_name,
            count=selling_count,
        ),
        200,
    )


@app.route('/<string:user_name>/portfolio')
def get_portfolio(user_name: str) -> tuple[Response, int]:
    response = jsonify(
        user_name=get_portfolio_with_filters(OperationsHistory.user_name == user_name)
    )
    return response, 200


@app.route('/<string:user_name>/history')
def show_history(user_name: str) -> Union[tuple[Response, int], tuple[str, int]]:
    limit = request.args.get(QueryParams.limit.value, type=int)
    page = request.args.get(QueryParams.page.value, type=int)
    if limit is None or page is None:
        return ErrorMessage.empty_input.value, 400
    with create_session() as session:
        showing_table = (
            session.query(OperationsHistory)
            .filter(
                OperationsHistory.user_name == user_name,
                OperationsHistory.id > limit * page,
            )
            .limit(limit)
            .all()
        )
        response = jsonify(showing_table)
    return response, 200


@app.route('/add', methods=['POST'])
def add_crypto() -> Union[tuple[Response, int], tuple[str, int]]:
    new_crypto_name = request.form.get(AddNewCryptoFormArgs.crypto_name.value)
    buy_price = request.form.get(AddNewCryptoFormArgs.buy_price.value)
    sell_price = request.form.get(AddNewCryptoFormArgs.sell_price.value)
    if new_crypto_name is None or buy_price is None or sell_price is None:
        return ErrorMessage.empty_input.value, 400
    with create_session() as session:
        new_crypto = Cryptocurrency(
            crypto_name=new_crypto_name,
            selling_price=sell_price,
            buying_price=buy_price,
            modification_date=datetime.now(),
        )
        session.merge(new_crypto)
    return (
        jsonify(added=new_crypto_name, buy_price=buy_price, sell_price=sell_price),
        200,
    )


thread1 = threading.Thread(target=change_currencies_rates, daemon=True)
thread1.start()
