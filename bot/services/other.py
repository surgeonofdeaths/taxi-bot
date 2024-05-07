from loguru import logger
import asyncio
from lexicon.lexicon import LEXICON, LEXICON_COMMANDS
from aiogram.types import KeyboardButton, Message
from aiogram.fsm.context import FSMContext
from sqlalchemy.ext.asyncio import AsyncSession
from services.helpcrunch import search_chat, get_assignee
from services.db_service import create_operator
from db.models import Order
from sqlalchemy import select
from states.state import Conversation

from keyboards.keyboard import get_menu_kb


def check_for_operator(telegram_id: int) -> None | dict:
    chat = search_chat(telegram_id)
    assignee = get_assignee(chat)
    return assignee


async def wait_for_operator(message: Message, state: FSMContext, session: AsyncSession) -> None:
    logger.info("Waiting for operator")

    while True:
        assignee = check_for_operator(message.from_user.id)

        if assignee:
            await create_operator(
                session=session,
                operator_id=assignee["id"],
                email=assignee["email"],
                name=assignee["name"],
                role=assignee["role"],
            )

            orders = select(Order).order_by(Order.id.desc())
            result = await session.execute(orders)
            order = result.first()[0]
            logger.info(order)
            order.operator_id = assignee["id"]

            btn_contact = KeyboardButton(text=LEXICON_COMMANDS.get("contact"))
            kb = get_menu_kb([btn_contact])

            await session.commit()
            await state.clear()
            # await state.set_state(Conversation.conversation)
            await message.answer(text=LEXICON.get("found_operator"), reply_markup=kb)
            break
        else:
            await asyncio.sleep(10)


def get_order_info(
    user_data: dict[str, any] | None = None, order_obj: Order | None = None
) -> str:
    if user_data:
        phone_number = user_data['phone_number']
        start_address = user_data['start_address']
        destination_address = user_data['destination_address']
        note = f"\nПожелание: {user_data['note']}" if user_data.get("note") else ""
    elif order_obj:
        phone_number = order_obj.user.phone_number
        start_address = order_obj.start_address
        destination_address = order_obj.destination_address
        note = f"\nПожелание: {order_obj.note}" if order_obj.note else ""
    else:
        # TODO: error
        return "Error"
    text = (
        f"Номер телефона: {phone_number}\nНачальный адрес: {start_address}\nАдрес прибытия: {destination_address}"
        + note
    )
    return text