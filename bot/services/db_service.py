from aiogram.types.user import User as UserType
from sqlalchemy import insert, select
from db.models import User, Order, Operator
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError
from aiogram.types import Message
from loguru import logger

from typing import Optional


async def db_add_to_db(item, session: AsyncSession):
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


async def db_create_user(user: Optional[UserType], session: AsyncSession):
    username = user.username if user.username else "no_username"
    user_entity = User(
        first_name=user.first_name,
        last_name=user.last_name,
        username=username,
        telegram_id=user.id,
    )
    await db_add_to_db(user_entity, session)


def get_users(id):
    users = select(User)
    print(users)
    return users


def create_user(user: Optional[UserType]):
    # if user.id not in get_users(user.id)
    get_users(user.id)

    # print(user.first_name, user.id)
    user_entity = insert(User).values(
        first_name=user.first_name,
        last_name=user.last_name,
        username=user.username,
        telegram_id=user.id,
    )
    return user_entity
