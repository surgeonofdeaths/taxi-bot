from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery
from loguru import logger
from services import db_create_user
from sqlalchemy.ext.asyncio import AsyncSession

from keyboards.factory_kb import TestCallbackFactory
from keyboards.keyboard import get_keyboard_markup


router = Router()


@router.callback_query(TestCallbackFactory.filter(F.name.startswith("te")))
async def process_callback_test(query: CallbackQuery):
    print(query)
    await query.answer(query.data)


@router.message(Command(commands=["start"]))
async def process_start_command(message: Message, session: AsyncSession):
    # keyboard_markup = 
    await db_create_user(message.from_user, session)
    await message.answer(
        "Добро пожаловать в бота для заказа такси!",
        # reply_markup=keyboard_markup.as_markup(),
    )


@router.message(Command(commands=["order"]))
async def process_order_command(message: Message):

    await message.answer("order")


@router.message()
async def process_wrong_text(message: Message):
    logger.info(f"User entered something else: {message.text}")
    await message.answer("some dummy data")
