from aiogram import F, Router
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import Message
from aiogram.utils.keyboard import KeyboardButton
from config.config import settings
from db.models import User
from keyboards.keyboard import get_menu_kb
from lexicon.lexicon import LEXICON, LEXICON_DB
from loguru import logger
from services.db_service import create_operator, get_or_create, populate_lexicon
from services.helpcrunch import (
    create_chat,
    create_customer,
    get_assignee,
    get_customer,
    get_user_state,
    search_chat,
)
from services.other import check_for_operator, get_user_filter
from services.state import set_main_state
from sqlalchemy.ext.asyncio import AsyncSession
from states.state import StartData

from bot.filters.filter import check_admin

router = Router()


# @router.message(StateFilter(None), Command(commands=["start"]))
# @router.message(StartData.start, Command(commands=["start"]))
@router.message(Command(commands=["start"]))
async def cmd_start(message: Message, state: FSMContext, session: AsyncSession):
    await state.clear()
    logger.info(await state.get_data())
    state_data = await set_main_state(message, session, state)
    logger.info(state_data)

    has_operator = state_data["has_operator"]
    is_admin = state_data["user"]["is_admin"]
    has_order = state_data["has_order"]

    kb = get_menu_kb(
        has_order=has_order,
        has_operator=has_operator,
        is_admin=is_admin,
    )
    await state.set_state(StartData.start)
    await message.answer(
        LEXICON["command_start"],
        reply_markup=kb,
    )


@router.message(StartData.start, Command(commands=["help"]))
@router.message(StartData.start, F.text == LEXICON["command_help"])
async def cmd_help(message: Message, state: FSMContext, session: AsyncSession):
    await message.answer(
        text=LEXICON["help"],
    )
