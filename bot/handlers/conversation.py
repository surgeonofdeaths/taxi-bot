import asyncio

from aiogram import F, Router
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import KeyboardButton, Message
from db.models import User
from keyboards.keyboard import get_kb_markup, get_menu_kb
from lexicon.lexicon import LEXICON, LEXICON_DB
from loguru import logger
from services.db_service import create_order
from services.helpcrunch import send_message
from services.other import check_for_operator, get_recent_messages_from_operator
from services.tasks import get_replies_from_operator
from sqlalchemy.ext.asyncio import AsyncSession
from states.state import Conversation, StartData

router = Router()


@router.message(StartData.start, Command(commands=["contact"]))
@router.message(StartData.start, F.text == LEXICON["command_contact"])
async def process_fsm_conversation_start(
    message: Message,
    state: FSMContext,
    session: AsyncSession,
):
    state_data = await state.get_data()
    # if state_data.get("has_operator") or check_for_operator(message.from_user.id):
    if state_data.get("has_operator"):
        buttons = [
            KeyboardButton(text=LEXICON["stop_conv"]),
        ]
        kb = get_kb_markup(*buttons)

        logger.info(state_data)
        chat_id = state_data["user"]["chat_id"]
        json = {
            "chat": chat_id,
            "text": LEXICON["user_started_conv_with_operator"],
            "type": "message",
        }

        created_message = send_message(json)

        task = asyncio.create_task(
            get_replies_from_operator(message, state, session),
            name="replies_from_operator",
        )
        await state.update_data(recent_message_id=created_message["id"])

        await message.answer(text=LEXICON["operator_conv"], reply_markup=kb)
        await state.set_state(Conversation.conversation)
    else:
        #  TODO: give phone numbers to the user
        text = "no contacts"
        await message.answer(text=text)


@router.message(Conversation.conversation, Command(commands=["stop"]))
@router.message(Conversation.conversation, F.text == LEXICON["stop_conv"])
async def process_fsm_stop_conversation(
    message: Message,
    state: FSMContext,
    session: AsyncSession,
):
    await state.set_state(StartData.start)
    state_data = await state.get_data()

    task = [
        task
        for task in asyncio.all_tasks()
        if task.get_name() == "replies_from_operator"
    ]
    logger.info(task)
    if task and task[0]:
        task[0].cancel()

    chat_id = state_data["user"]["chat_id"]
    json = {
        "chat": chat_id,
        "text": LEXICON["user_stopped_conv_with_operator"],
        "type": "message",
    }
    send_message(json)

    kb = get_menu_kb(
        has_order=state_data.get("has_order"),
        has_operator=state_data.get("has_operator"),
        is_admin=state_data["user"]["is_admin"],
    )
    await message.answer(text=LEXICON["conv_stopped"], reply_markup=kb)


@router.message(Conversation.conversation)
async def process_fsm_conversation(
    message: Message,
    state: FSMContext,
    session: AsyncSession,
):
    state_data = await state.get_data()
    chat_id = state_data["user"]["chat_id"]
    text = message.text
    if text:
        user_json = {"chat": chat_id, "text": text, "type": "message"}
        created_message = send_message(user_json)
        logger.info(created_message)
    else:
        await message.answer(text=LEXICON_DB["only_text"])
