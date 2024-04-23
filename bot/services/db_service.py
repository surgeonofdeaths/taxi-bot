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
        await session.refresh(item)  # check
        logger.info(f"{item.username}: has been added to the database")
        return True
    except IntegrityError:
        await session.rollback()
        logger.info(f"{item.username}: already exists!")
        return False


async def create_user(user: Optional[UserType], session: AsyncSession):
    chat_id = search_customer(user.id)["data"][0]["id"]
    username = user.username if user.username else "no_username"
    user_entity = User(
        chat_id=chat_id,
        first_name=user.first_name,
        last_name=user.last_name,
        username=username,
        telegram_id=user.id,
    )
    await add_to_db(user_entity, session)


async def get_user(telegram_id: int, session: AsyncSession):
    query = select(User).where(User.telegram_id == telegram_id).limit(1)
    first_user = await session.execute(query)
    return first_user.scalars().first()


async def create_order(telegram_id: int, session: AsyncSession):
    return


async def create_order(
    session: AsyncSession,
    user_id: int,
    operator_id: int,
    note: str,
    start_address: str,
    destination_address: str,
    price: int,
    car_mark: str,
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
    await add_to_db(new_order)
