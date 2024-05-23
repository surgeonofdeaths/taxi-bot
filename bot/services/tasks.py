import asyncio

from aiogram.fsm.context import FSMContext
from aiogram.types import KeyboardButton, Message
from db.models import Order
from keyboards.keyboard import get_menu_kb
from lexicon.lexicon import LEXICON
from loguru import logger
from services.db_service import create_operator
from services.helpcrunch import get_messages
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from states.state import StartData

from .other import check_for_operator, get_recent_messages_from_operator


async def wait_for_operator(
    message: Message, state: FSMContext, session: AsyncSession
) -> None:
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
            # logger.info(order)
            order.operator_id = assignee["id"]

            contact_btn = KeyboardButton(text=LEXICON.get("command_contact"))
            state_data = await state.get_data()
            kb = get_menu_kb(
                [contact_btn],
                has_order=True,
                is_admin=state_data.get("user").get("is_admin"),
            )

            await state.set_state(StartData.start)
            await session.commit()
            await state.update_data(has_operator=True)
            await message.answer(text=LEXICON.get("found_operator"), reply_markup=kb)
            break
        else:
            await asyncio.sleep(5)


async def get_replies_from_operator(
    message: Message, state: FSMContext, session: AsyncSession
) -> None:
    logger.info("Waiting to hear from operator!")

    while True:
        state_data = await state.get_data()
        # logger.info(state_data["recent_message_id"])
        messages = get_messages(state_data["user"].chat_id)
        recent_messages = get_recent_messages_from_operator(
            state_data["recent_message_id"], messages
        )
        logger.info(recent_messages)

        [
            await message.answer(text=recent_message.get("text"))
            for recent_message in recent_messages
        ]
        await state.update_data(recent_message_id=messages[0]["id"])
        await asyncio.sleep(10)
