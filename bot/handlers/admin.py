import asyncio

from aiogram import F, Router
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, KeyboardButton, Message
from aiogram.utils.keyboard import (
    InlineKeyboardBuilder,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
)
from filters.filter import IsAdmin
from keyboards.factory_kb import LexiconCallbackFactory
from keyboards.keyboard import build_inline_kb
from lexicon.lexicon import LEXICON, LEXICON_DB
from loguru import logger
from services.db_service import get_or_create
from sqlalchemy.ext.asyncio import AsyncSession
from states.state import StartData

router = Router()


@router.callback_query(F.data == "admin_menu")
@router.message(StartData.start, IsAdmin(), Command(commands=["admin"]))
@router.message(StartData.start, IsAdmin(), F.text == LEXICON["command_admin"])
async def cmd_admin(message: Message, state: FSMContext, session: AsyncSession):
    btns = [
        InlineKeyboardButton(
            text=LEXICON["admin_admins"], callback_data="admin_admins"
        ),
        InlineKeyboardButton(
            text=LEXICON["admin_lexicon"], callback_data="admin_lexicon"
        ),
    ]
    kb = build_inline_kb(*btns)

    await message.answer(text=LEXICON["admin_panel"], reply_markup=kb)
    # await message.edit_reply_markup(text=LEXICON["admin_panel"], reply_markup=kb)


@router.callback_query(F.data == "admin_admins")
async def process_admin_btn(
    callback: CallbackQuery, state: FSMContext, session: AsyncSession
):
    await callback.message.answer(text="admins")


@router.callback_query(F.data == "admin_lexicon")
async def process_lexicon_btn(
    callback: CallbackQuery, state: FSMContext, session: AsyncSession
):
    btns = [
        InlineKeyboardButton(
            text=key,
            callback_data=LexiconCallbackFactory(key=key).pack(),
        )
        for key in LEXICON.keys()
    ]
    btns.append(
        InlineKeyboardButton(text=LEXICON["admin_go_back"], callback_data="admin_menu")
    )
    kb = build_inline_kb(*btns, adjust=4)
    await callback.message.answer(text="lexicon", reply_markup=kb)
