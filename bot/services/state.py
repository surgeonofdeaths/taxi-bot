from aiogram.fsm.context import FSMContext
from aiogram.types import Message
from loguru import logger
from sqlalchemy.ext.asyncio import AsyncSession

from bot.services.db_service import get_unprocessed_order
from bot.services.helpcrunch import get_user_state
from bot.services.other import check_for_operator


async def set_main_state(
    message: Message, session: AsyncSession, state: FSMContext
) -> dict:
    has_order = bool(await get_unprocessed_order(message.from_user.id, session))
    has_operator = check_for_operator(message.from_user.id)

    user_state = await get_user_state(message, session)

    await state.update_data(
        user=user_state,
        has_operator=has_operator,
        has_order=has_order,
    )
    updated_state = await state.get_data()
    logger.info(updated_state)
    return updated_state
