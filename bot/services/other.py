import requests
from loguru import logger
import asyncio
from lexicon.lexicon import LEXICON, LEXICON_COMMANDS
from aiogram.types import CallbackQuery, KeyboardButton, Message, ReplyKeyboardMarkup
from aiogram.fsm.context import FSMContext
from sqlalchemy.ext.asyncio import AsyncSession
from services.helpcrunch import search_chat, get_assignee
from services.db_service import create_operator
from db.models import Order
from sqlalchemy import select

from keyboards.keyboard import get_kb_markup, get_menu_kb


async def wait_for_operator(message: Message, state: FSMContext, session: AsyncSession):
    logger.info("Waiting for operator")

    while True:
        chat = search_chat(message.from_user.id)
        assignee = get_assignee(chat)
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

            kb = get_menu_kb()

            await session.commit()
            await state.clear()
            await message.answer(text=LEXICON.get("found_operator"), reply_markup=kb)
            break
        else:
            await asyncio.sleep(10)
