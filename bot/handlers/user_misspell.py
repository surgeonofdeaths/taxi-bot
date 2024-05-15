from aiogram import Router
from aiogram.types import Message
from lexicon.lexicon import LEXICON
from loguru import logger

router = Router()


@router.message()
async def process_wrong_text(message: Message):
    logger.info(f"User entered something else: {message.text}")
    await message.answer(LEXICON.get("user_misspell"))
