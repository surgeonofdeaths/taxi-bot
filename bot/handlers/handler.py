from aiogram import Router
from aiogram.types import Message

from aiogram.filters import Command
from loguru import logger

router = Router()


@router.message(Command(commands=["start"]))
async def process_start_command(message: Message):
    await message.answer("Добро пожаловать в бота для заказа такси!")


@router.message()
async def process_wrong_text(message: Message):
    logger.info(f"User entered something else: {message.text}")
    await message.answer("some dummy data")
