from aiogram import F, Router
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message
from keyboards.keyboard import get_menu_kb
from lexicon.lexicon import LEXICON
from loguru import logger
from services.state import set_main_state
from sqlalchemy.ext.asyncio import AsyncSession
from states.state import StartData

router = Router()


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
async def cmd_help(message: Message):
    await message.answer(
        text=LEXICON["help"],
    )
