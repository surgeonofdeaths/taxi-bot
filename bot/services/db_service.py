from typing import Optional

from aiogram.types import Message
from aiogram.types.user import User as UserType
from db.models import Lexicon, Operator, Order
from lexicon.lexicon import LEXICON, LEXICON_DB
from loguru import logger
from services.helpcrunch import search_customer
from sqlalchemy import exists, insert, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession


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


# async def create_user(user: Optional[UserType], chat_id: str, session: AsyncSession):
#     chat = search_customer(user.id)
#     logger.info(chat)
#     logger.info(user.id)
#     customer_id = chat["data"][0]["id"]
#     username = user.username if user.username else "no_username"
#     user_entity = User(
#         id=user.id,
#         customer_id=str(customer_id),
#         chat_id=str(chat_id),
#         first_name=user.first_name,
#         last_name=user.last_name,
#         username=username,
#     )
# await add_to_db(user_entity, session)


async def create_order(
    session: AsyncSession,
    user_id: int,
    start_address: str,
    destination_address: str,
    message_id: int,
    note: str | None = None,
    operator_id: int | None = None,
):
    order = Order(
        user_id=user_id,
        operator_id=operator_id,
        note=note,
        start_address=start_address,
        destination_address=destination_address,
        message_id=message_id,
    )
    await add_to_db(order, session)


async def create_operator(
    session: AsyncSession,
    operator_id: int,
    name: str,
    email: str,
    role: str,
):
    operator = Operator(
        id=operator_id,
        name=name,
        email=email,
        role=role,
    )
    await add_to_db(operator, session)


async def get_unprocessed_order(telegram_id: str, session) -> None | Order:
    any_unprocessed_order_query = select(Order).where(
        Order.user_id == telegram_id,
        Order.processed == False,  # noqa
    )
    any_unprocessed_orders = await session.execute(any_unprocessed_order_query)
    any_unprocessed_order = any_unprocessed_orders.first()
    if any_unprocessed_order:
        return any_unprocessed_order[0]


def get_user_filter(**kwargs) -> dict:
    user = kwargs["user"]
    chat = search_customer(user.id)
    customer_id = chat["data"][0]["id"]
    username = user.username if user.username else "no_username"
    filter = {}
    filter["id"] = user.id
    filter["username"] = username
    filter["first_name"] = user.first_name
    filter["last_name"] = user.last_name
    filter["customer_id"] = str(customer_id)
    filter["chat_id"] = str(kwargs["chat_id"])
    logger.info(filter)
    return filter


async def get_or_create(session: AsyncSession, model, filter: dict):
    query = select(model).filter_by(**filter)
    instances = await session.execute(query)
    logger.info(instances)
    try:
        instance = instances.first()[0]
    except TypeError:
        instance = None
    if instance:
        logger.info("Instance exists")
        return instance
    else:
        instance = model(**filter)
        session.add(instance)
        await session.commit()
        logger.info("Instance created")
        return instance


async def populate_lexicon(session: AsyncSession):
    for key, value in LEXICON.items():
        lexicon_obj = await get_or_create(session, Lexicon, {"key": key, "text": value})
        LEXICON_DB[key] = value
