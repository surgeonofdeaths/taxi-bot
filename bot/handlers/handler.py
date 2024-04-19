from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message
from loguru import logger
from services import db_create_user
from sqlalchemy.ext.asyncio import AsyncSession

router = Router()


@router.message(Command(commands=["start"]))
async def process_start_command(message: Message, session: AsyncSession):
    await db_create_user(message.from_user, session)
    await message.answer("Добро пожаловать в бота для заказа такси!")


@router.message(Command(commands=["order"]))
async def process_order_command(message: Message):
    await message.answer("order")


@router.message()
async def process_wrong_text(message: Message):
    logger.info(f"User entered something else: {message.text}")
    await message.answer("some dummy data")
