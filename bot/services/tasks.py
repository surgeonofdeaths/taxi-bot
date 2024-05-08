from loguru import logger
import asyncio
from lexicon.lexicon import LEXICON, LEXICON_COMMANDS
from aiogram.types import KeyboardButton, Message
from aiogram.fsm.context import FSMContext
from sqlalchemy.ext.asyncio import AsyncSession
from services.db_service import create_operator
from db.models import Order
from sqlalchemy import select
from states.state import StartData
from .other import check_for_operator, check_for_messages
from keyboards.keyboard import get_menu_kb
from services.helpcrunch import get_message


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
            logger.info(order)
            order.operator_id = assignee["id"]

            contact_btn = KeyboardButton(text=LEXICON_COMMANDS.get("contact"))
            kb = get_menu_kb([contact_btn], has_order=True)

            await session.commit()
            await state.set_state(StartData.start)
            await state.update_data(has_operator=True)
            await message.answer(text=LEXICON.get("found_operator"), reply_markup=kb)
            break
        else:
            await asyncio.sleep(10)


async def get_replies_from_operator(
    message: Message, state: FSMContext, session: AsyncSession
) -> None:
    logger.info("Waiting to hear from operator!")
    state_data = await state.get_data()

    while True:
        message = get_message(state_data["user"].chat_id)
        print(message)
        await asyncio.sleep(10)
        # assignee = check_for_operator(message.from_user.id)

        # if assignee:
        #     await create_operator(
        #         session=session,
        #         operator_id=assignee["id"],
        #         email=assignee["email"],
        #         name=assignee["name"],
        #         role=assignee["role"],
        #     )

        #     orders = select(Order).order_by(Order.id.desc())
        #     result = await session.execute(orders)
        #     order = result.first()[0]
        #     logger.info(order)
        #     order.operator_id = assignee["id"]

        #     contact_btn = KeyboardButton(text=LEXICON_COMMANDS.get("contact"))
        #     kb = get_menu_kb([contact_btn], has_order=True)

        #     await session.commit()
        #     await state.set_state(StartData.start)
        #     await state.update_data(has_operator=True)
        #     await message.answer(text=LEXICON.get("found_operator"), reply_markup=kb)
        #     break
        # else:
        #     await asyncio.sleep(10)
