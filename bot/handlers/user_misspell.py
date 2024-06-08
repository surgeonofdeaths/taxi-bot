from aiogram import Router
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import Message
from lexicon.lexicon import LEXICON
from loguru import logger
from services.state import set_main_state
from sqlalchemy.ext.asyncio import AsyncSession

from bot.keyboards.keyboard import get_menu_kb
from bot.states.state import StartData

router = Router()


@router.message(Command(commands=["reboot"]))
async def process_bot_reboot(message: Message, state: FSMContext):
    #  TODO: more elegant way to set state after reboot without "/start" command
    logger.info("Reboot")
    logger.info("Previous state:")
    logger.info(await state.get_data())
    await state.clear()
    await message.reply(text="Повторите запрос! Бот был перезапущен.")


@router.message()
async def process_wrong_text(
    message: Message, state: FSMContext, session: AsyncSession
):
    logger.info(f"User entered something else: {message.text}")
    state_state = await state.get_state()
    state_data = await state.get_data()
    logger.info(state_state)
    logger.info(state_data)

    # if message.text in (LEXICON["command_admin"], "/admin"):
    #     is_admin = False
    #
    # if message.text in (LEXICON["command_contact"], "/contact"):
    #     has_operator = False
    #
    # kb = get_menu_kb(
    #     has_operator=has_operator,
    #     is_admin=is_admin,
    # )

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
    await message.answer(LEXICON.get("user_misspell"), reply_markup=kb)
