from aiogram.fsm.context import FSMContext
from aiogram.types import Message
from loguru import logger
from sqlalchemy.ext.asyncio import AsyncSession

from bot.filters.filter import check_admin
from bot.services.helpcrunch import get_or_create_customer_user
from bot.services.other import check_for_operator


async def set_main_state(message: Message, session: AsyncSession, state: FSMContext):
    state_data = await state.get_data()
    logger.info(state_data)
    customer = state_data.get("customer")
    user = state_data.get("user")
    has_operator = state_data.get("has_operator")
    has_order = state_data.get("has_order")
    is_admin = state_data.get("is_admin")
    user = await get_or_create_customer_user(message, session, user)

    if not has_operator:
        has_operator = check_for_operator(message.from_user.id)

    is_admin = await check_admin(session, message, user)

    await state.update_data(
        customer=customer,
        user=user,
        has_operator=has_operator,
        is_admin=is_admin,
        has_order=has_order,
    )
    updated_state = await state.get_data()
    return updated_state
