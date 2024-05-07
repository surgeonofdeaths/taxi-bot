from aiogram import F, Router
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import KeyboardButton, Message
from keyboards.keyboard import get_kb_markup, get_menu_kb
from loguru import logger
from sqlalchemy.ext.asyncio import AsyncSession
from states.state import Conversation
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


@router.message(StateFilter(None), Command(commands=["contact"]))
@router.message(StateFilter(None), F.text == LEXICON_COMMANDS["contact"])
async def process_fsm_conversation(
    message: Message,
    state: FSMContext,
    session: AsyncSession,
):
    check = check_for_operator(message.from_user.id)
    if check:
        buttons = [
            KeyboardButton(text=LEXICON["stop_conv"]),
        ]
        kb = get_kb_markup(*buttons)
        await state.set_state(Conversation.conversation)
        await message.answer(text=LEXICON["operator_conv"], kb=kb)
    else:
        # TODO: give phone numbers to the user
        text = "no contacts"
        await message.answer(text=text)
