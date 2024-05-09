import asyncio

from aiogram.fsm.context import FSMContext
from aiogram.types import KeyboardButton, Message
from db.models import Order
from keyboards.keyboard import get_menu_kb
from lexicon.lexicon import LEXICON, LEXICON_COMMANDS
from loguru import logger
from services.db_service import create_operator
from services.helpcrunch import get_assignee, get_messages, search_chat
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from states.state import Conversation, StartData


def check_for_operator(telegram_id: int) -> None | dict:
    chat = search_chat(telegram_id)
    assignee = get_assignee(chat)
    return assignee


def get_order_info(
    user_data: dict[str, any] | None = None, order_obj: Order | None = None
) -> str:
    if user_data:
        phone_number = user_data["phone_number"]
        start_address = user_data["start_address"]
        destination_address = user_data["destination_address"]
        note = f"\nПожелание: {user_data['note']}" if user_data.get("note") else ""
    elif order_obj:
        phone_number = order_obj.user.phone_number
        start_address = order_obj.start_address
        destination_address = order_obj.destination_address
        note = f"\nПожелание: {order_obj.note}" if order_obj.note else ""
    else:
        #  TODO: error
        return "Error"
    text = (
        f"Номер телефона: {phone_number}\nНачальный адрес: {start_address}\nАдрес прибытия: {destination_address}"
        + note
    )
    return text


def get_recent_messages_from_operator(recent_message_id: int, messages: dict) -> dict:
    roles = ("admin", "operator", "agent")
    recent_messages = []

    diff = int(messages[0].get("id")) - recent_message_id
    [
        recent_messages.append(messages[i])
        for i in range(diff)
        if messages[i]["from"] in roles and messages[i]["type"] == "message"
    ]
    return recent_messages
