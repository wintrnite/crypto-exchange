from contextlib import contextmanager
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any

import sqlalchemy as sa
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from app.constants import Files

engine = sa.create_engine('sqlite:///app.db')
Base = declarative_base()


@contextmanager
def create_session(**kwargs: Any) -> sessionmaker:
    new_session = Session(**kwargs)
    try:
        yield new_session
        new_session.commit()
    except Exception:
        new_session.rollback()
        raise
    finally:
        new_session.close()


@dataclass
class Cryptocurrency(Base):  # type: ignore
    crypto_name: str
    selling_price: str
    buying_price: str
    modification_date: datetime
    __tablename__ = 'cryptocurrency'

    id = sa.Column(sa.Integer, primary_key=True)
    crypto_name = sa.Column(sa.String(), unique=True, nullable=False)
    selling_price = sa.Column(sa.String(), nullable=False)
    buying_price = sa.Column(sa.String(), nullable=False)
    modification_date = sa.Column(sa.DateTime())


@dataclass
class User(Base):  # type: ignore
    user_name: str
    balance: str
    __tablename__ = 'user'

    id = sa.Column(sa.Integer, primary_key=True)
    user_name = sa.Column(sa.String(), unique=True, nullable=False)
    balance = sa.Column(sa.String())


@dataclass
class OperationsHistory(Base):  # type: ignore
    user_name: str
    operation: str
    crypto_name: str
    count: str
    __tablename__ = 'operation_history'

    id = sa.Column(sa.Integer, primary_key=True)
    user_name = sa.Column(sa.Integer, sa.ForeignKey('user.user_name'))
    operation = sa.Column(sa.String())
    crypto_name = sa.Column(sa.String(), sa.ForeignKey('cryptocurrency.crypto_name'))
    count = sa.Column(sa.String())


Session = sessionmaker(bind=engine)


def init_db(base: declarative_base, db_engine: sa.create_engine) -> None:
    if not Path(Files.db.value).is_file():
        base.metadata.create_all(db_engine)  # type: ignore
        with create_session() as session:
            cryptocurrencies = (
                Cryptocurrency(
                    crypto_name='bitcoin',
                    selling_price='2000',
                    buying_price='3000',
                    modification_date=datetime.now(),
                ),
                Cryptocurrency(
                    crypto_name='wipcoin',
                    selling_price='20',
                    buying_price='30',
                    modification_date=datetime.now(),
                ),
                Cryptocurrency(
                    crypto_name='litcoin',
                    selling_price='6000',
                    buying_price='10000',
                    modification_date=datetime.now(),
                ),
                Cryptocurrency(
                    crypto_name='stickcoin',
                    selling_price='20',
                    buying_price='3000',
                    modification_date=datetime.now(),
                ),
                Cryptocurrency(
                    crypto_name='benzcoin',
                    selling_price='300',
                    buying_price='301',
                    modification_date=datetime.now(),
                ),
            )
            session.add_all(cryptocurrencies)
