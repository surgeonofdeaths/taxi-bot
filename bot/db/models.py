import asyncio
from datetime import datetime

from .base import Base
from .database import engine
from sqlalchemy import (
    CHAR,
    BigInteger,
    Boolean,
    Column,
    ForeignKey,
    Integer,
    String,
    Text,
    DateTime,
)
from sqlalchemy.orm import relationship


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    chat_id = Column(Integer)
    first_name = Column(String(length=255), nullable=True)
    last_name = Column(String(length=255), nullable=True)
    username = Column(String(length=255), nullable=False)
    phone_number = Column(String(length=255), nullable=True)
    telegram_id = Column(BigInteger, nullable=False, unique=True)
    admin = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow())
    updated_at = Column(DateTime, default=datetime.utcnow)

    def __str__(self):
        return f"{self.__class__.__name__}<id={self.id}, username={self.username}>"


class Operator(Base):
    __tablename__ = "operators"

    id = Column(Integer, primary_key=True, index=True)
    phone_number = Column(String(length=255), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow())
    updated_at = Column(DateTime, default=datetime.utcnow)

    def __str__(self):
        return f"<id={self.id}, phone={self.phone_number}>"


class Order(Base):
    __tablename__ = "orders"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    operator_id = Column(Integer, ForeignKey("operators.id"))
    note = Column(Text())
    processed = Column(Boolean, default=False)
    start_address = Column(CHAR(length=256))
    destination_address = Column(CHAR(length=256))
    price = Column(Integer, nullable=True)
    number_of_people = Column(Integer, nullable=True)  # TODO: do I need this field?
    car_mark = Column(CHAR(length=256))
    created_at = Column(DateTime, default=datetime.utcnow())
    updated_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", backref="orders")
    operator = relationship("Operator", backref="orders")

    def __str__(self):
        return f"{self.__class__.__name__}<id={self.id}, name={self.user_id}>"


# async def init_models():
#     async with engine.begin() as conn:
#         await conn.run_sync(Base.metadata.drop_all)
#         await conn.run_sync(Base.metadata.create_all)


# asyncio.run(init_models())
