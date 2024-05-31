from aiogram import Router
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import Message
from lexicon.lexicon import LEXICON
from loguru import logger
from services.state import set_main_state
from sqlalchemy.ext.asyncio import AsyncSession

from bot.states.state import StartData

router = Router()


@router.message(Command(commands=["reboot"]))
async def process_bot_reboot(
    message: Message, session: AsyncSession, state: FSMContext
):
    #  TODO: more elegant way to set state after reboot without "/start" command
    logger.info("Reboot")
    await state.clear()
    # await state.set_state(StartData.start)
    # state_data = await set_main_state(message, session, state)
    # logger.info(state_data)
    await message.reply(text="Повторите запрос! Бот был пере")


@router.message()
async def process_wrong_text(message: Message, state: FSMContext):
    logger.info(f"User entered something else: {message.text}")
    state_state = await state.get_state()
    state_data = await state.get_data()
    logger.info(state_state)
    logger.info(state_data)
    await message.answer(LEXICON.get("user_misspell"))
