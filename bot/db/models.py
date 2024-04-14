import asyncio
from datetime import datetime

from db.base import Base
from db.database import engine
from sqlalchemy import (CHAR, BigInteger, Boolean, Column, ForeignKey, Integer,
                        String, Text)
from sqlalchemy.orm import relationship


class CommonFields(Base):
    __tablename__ = "common_fields"

    id = Column(Integer, primary_key=True, index=True)
    created_at = Column(default=datetime.utcnow())
    updated_at = Column(default_factory=datetime.utcnow)


class User(CommonFields, Base):
    __tablename__ = "users"

    # id = Column(Integer, primary_key=True, index=True)
    name = Column(String(length=255), nullable=True)
    username = Column(String(length=255), nullable=False)
    phone_number = Column(String(length=255), nullable=True)
    telegram_id = Column(BigInteger, nullable=False)
    admin = Column(Boolean, default=False)

    # created_at = Column(default=datetime.utcnow())
    # updated_at = Column(default_factory=datetime.utcnow)

    def __str__(self):
        return f"{self.__class__.__name__}<id={self.id}, name={self.name}>"


class Operator(CommonFields, Base):
    __tablename__ = "operators"

    # id = Column(Integer, primary_key=True, index=True)
    phone_number = Column(String(length=255), nullable=True)

    # created_at = Column(default=datetime.utcnow())
    # updated_at = Column(default_factory=datetime.utcnow)

    def __str__(self):
        return f"<id={self.id}, phone={self.phone_number}>"


class Order(CommonFields, Base):
    __tablename__ = "operators"

    user_id = Column(Integer, ForeignKey("users.id"))
    operator_id = Column(Integer, ForeignKey("operators.id"))
    note = Column(Text(length=1000))
    processed = Column(Boolean, default=False)
    start_address = Column(CHAR(length=256))
    destination_address = Column(CHAR(length=256))
    price = Column(Integer, nullable=True)
    number_of_people = Column(Integer, nullable=True)
    car_mark = Column(CHAR(length=256))

    user = relationship("User", backref="orders")
    operator = relationship("Operator", backref="orders")


async def init_models():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)


asyncio.run(init_models())
