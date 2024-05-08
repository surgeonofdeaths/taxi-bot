from aiogram import F, Router
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import KeyboardButton, Message
from keyboards.keyboard import get_kb_markup, get_menu_kb
from loguru import logger
from sqlalchemy.ext.asyncio import AsyncSession
from states.state import Conversation, StartData
from lexicon.lexicon import LEXICON
from services.helpcrunch import (
    send_message,
)
from services.other import wait_for_operator, check_for_operator
from services.db_service import create_order
from db.models import User
import asyncio
from lexicon.lexicon import LEXICON_COMMANDS

router = Router()


@router.message(StartData.start, Command(commands=["contact"]))
@router.message(StartData.start, F.text == LEXICON_COMMANDS["contact"])
async def process_fsm_conversation_start(
    message: Message,
    state: FSMContext,
    session: AsyncSession,
):
    state_data = await state.get_data()
    if state_data.get("has_operator") or check_for_operator(message.from_user.id):
        buttons = [
            KeyboardButton(text=LEXICON["stop_conv"]),
        ]
        kb = get_kb_markup(*buttons)
        logger.info(kb)

        await message.answer(text=LEXICON["operator_conv"], kb=kb)
        await state.set_state(Conversation.conversation)
    else:
        # TODO: give phone numbers to the user
        text = "no contacts"
        await message.answer(text=text)


@router.message(Conversation.conversation, F.text == LEXICON["operator_conv"])
async def process_fsm_conversation(
    message: Message,
    state: FSMContext,
    session: AsyncSession,
):
    await message.answer(text="sfsdf")


@router.message(Conversation.conversation, Command(commands=["stop"]))
@router.message(Conversation.conversation, F.text == LEXICON["stop_conv"])
async def process_fsm_stop_conversation(
    message: Message,
    state: FSMContext,
    session: AsyncSession,
):
    state.set_state(StartData.start)
    await message.answer(text=LEXICON["conv_stopped"])
