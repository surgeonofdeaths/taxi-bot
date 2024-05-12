import asyncio

from aiogram import F, Router
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import KeyboardButton, Message
from filters.filter import IsAdmin
from lexicon.lexicon import LEXICON, LEXICON_DB
from services.db_service import get_or_create
from sqlalchemy.ext.asyncio import AsyncSession
from states.state import StartData

router = Router()


@router.message(StartData.start, IsAdmin(), Command(commands=["admin"]))
async def process_fsm_cancel_order(
    message: Message, state: FSMContext, session: AsyncSession
):
    await message.answer(text="logged as admin!")
