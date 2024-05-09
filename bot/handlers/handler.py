from aiogram import F, Router
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import Message
from aiogram.utils.keyboard import KeyboardButton
from db.models import User
from keyboards.keyboard import get_menu_kb
from lexicon.lexicon import LEXICON
from services.db_service import create_operator, get_or_create, get_user_filter
from services.helpcrunch import (
    create_chat,
    create_customer,
    get_assignee,
    get_customer,
    search_chat,
)
from services.other import check_for_operator

# from loguru import logger
from sqlalchemy.ext.asyncio import AsyncSession
from states.state import StartData

router = Router()


@router.message(StateFilter(None), Command(commands=["start"]))
@router.message(StartData.start, Command(commands=["start"]))
async def cmd_start(message: Message, state: FSMContext, session: AsyncSession):
    state_data = await state.get_data()
    if not state_data.get("has_operator"):
        # logger.info(state_data.get("has_operator"))
        check = check_for_operator(message.from_user.id)
        if check:
            # logger.info(check)
            await state.update_data(has_operator=True)

    if not any(
        [state_data.get("customer"), state_data.get("chat"), state_data.get("user")]
    ):
        customer = get_customer(message.from_user.id)
        if customer and customer.get("data"):
            chat = customer["data"][0]
        else:
            print(customer)
            customer = create_customer(
                message.from_user.id, message.from_user.full_name
            )
            chat = create_chat(customer["id"])

        filter = get_user_filter(
            user=message.from_user,
            chat_id=chat["id"],
        )
        user = await get_or_create(
            session,
            User,
            filter,
        )
        await state.update_data(customer=customer, chat=chat, user=user)
    kb = get_menu_kb(
        has_order=state_data.get("has_order"),
        has_operator=state_data.get("has_operator"),
    )
    await state.set_state(StartData.start)
    await message.answer(
        LEXICON.get("command_start"),
        reply_markup=kb,
    )


@router.message(StartData.start, Command(commands=["help"]))
@router.message(StartData.start, F.text == LEXICON["command_help"])
async def cmd_help(message: Message, state: FSMContext, session: AsyncSession):
    await message.answer(
        text=LEXICON.get("command_help"),
    )
