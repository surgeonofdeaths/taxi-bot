from aiogram import F, Router
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import Message
from keyboards.keyboard import get_menu_kb
from loguru import logger
from services import create_user
from sqlalchemy.ext.asyncio import AsyncSession
from lexicon.lexicon import LEXICON_COMMANDS
from services.helpcrunch import (
    create_customer,
    create_chat,
    get_customer,
    search_chat,
)
from services.helpcrunch import get_assignee
from services.db_service import create_operator

router = Router()


@router.message(StateFilter(None), Command(commands=["start"]))
async def cmd_start(message: Message, session: AsyncSession):
    kb = get_menu_kb()
    customer = get_customer(message.from_user.id)
    if customer and customer.get("data"):
        logger.info(customer)

        chat = customer["data"][0]
    else:
        customer = create_customer(
            message.from_user.id, message.from_user.full_name
        )
        chat = create_chat(customer["id"])
    await create_user(message.from_user, chat["id"], session)
    await message.answer(
        LEXICON_COMMANDS.get("start"),
        reply_markup=kb,
    )


@router.message(StateFilter(None), Command(commands=["help"]))
@router.message(StateFilter(None), F.text == LEXICON_COMMANDS["help"])
async def cmd_help(message: Message, state: FSMContext, session: AsyncSession):
    await message.answer(
        text=LEXICON_COMMANDS.get("help"),
    )
