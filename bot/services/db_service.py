from db.models import Lexicon, Operator, Order, User
from lexicon.lexicon import LEXICON
from loguru import logger
from sqlalchemy import select, update
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


async def get_or_create(session: AsyncSession, model, filter: dict):
    query = select(model).filter_by(**filter)
    instances = await session.execute(query)
    try:
        instance = instances.first()[0]
    except TypeError:
        instance = None
    if instance:
        return instance
    else:
        logger.info(filter)
        instance = model(**filter)
        session.add(instance)
        await session.commit()
        return instance


async def get_or_create_lexicon_object(session: AsyncSession, filter: dict):
    query = select(Lexicon).where(Lexicon.key == filter["key"])
    instance = await session.execute(query)
    instance = instance.scalar_one_or_none()

    if not instance:
        instance = Lexicon(**filter)
        session.add(instance)
        await session.commit()
    return instance


async def populate_lexicon(session: AsyncSession):
    for key, text in LEXICON.items():
        lexicon_obj = await get_or_create_lexicon_object(
            session, {"key": key, "text": text}
        )
        LEXICON[key] = lexicon_obj.text


async def update_lexicon_obj(session: AsyncSession, data: dict):
    instance = await session.execute(
        update(Lexicon).where(Lexicon.key == data["key"]).values(text=data["text"])
    )
    await session.commit()
    return instance


async def get_admin_users(session: AsyncSession):
    query = select(User).where(User.admin == True)  # noqa
    instances = await session.execute(query)
    admins = [admin[0] for admin in instances if admin]
    return admins


async def check_if_model_exists(session, model, filter):
    query = select(model).filter_by(**filter)
    instances = await session.execute(query)
    try:
        instance = instances.first()[0]
    except TypeError:
        instance = None
    return instance
