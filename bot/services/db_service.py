from aiogram.types.user import User as UserType
from sqlalchemy import insert, select
from db.models import User, Order, Operator
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError
from aiogram.types import Message
from loguru import logger

from typing import Optional
from services.helpcrunch import search_customer


async def add_to_db(item, session: AsyncSession):
    session.add(item)

    try:
        await session.commit()
        await session.refresh(item)
        logger.info(f"{item}: has been added to the database")
        return True
    except IntegrityError:
        await session.rollback()
        logger.info(f"{item}: already exists!")
        return False


async def create_user(user: Optional[UserType], chat_id: str, session: AsyncSession):
    chat = search_customer(user.id)
    logger.info(chat)
    logger.info(user.id)
    customer_id = chat["data"][0]["id"]
    username = user.username if user.username else "no_username"
    user_entity = User(
        id=user.id,
        customer_id=str(customer_id),
        chat_id=str(chat_id),
        first_name=user.first_name,
        last_name=user.last_name,
        username=username,
    )
    await add_to_db(user_entity, session)


async def create_order(
    session: AsyncSession,
    user_id: int,
    note: str,
    start_address: str,
    destination_address: str,
    price: int | None = None,
    car_mark: str | None = None,
    operator_id: int | None = None,
):
    # Create a new order object
    new_order = Order(
        user_id=user_id,
        operator_id=operator_id,
        note=note,
        start_address=start_address,
        destination_address=destination_address,
        price=price,
        car_mark=car_mark,
    )
    await add_to_db(new_order, session)
