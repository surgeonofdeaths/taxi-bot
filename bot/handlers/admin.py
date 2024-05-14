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
from keyboards.keyboard import build_inline_kb, get_admin_menu_kb, get_lexicon_objs_kb
from lexicon.lexicon import LEXICON, LEXICON_DB
from loguru import logger
from services.db_service import get_or_create, update_lexicon_obj
from sqlalchemy.ext.asyncio import AsyncSession
from states.state import Lexicon, StartData

router = Router()


@router.message(StartData.start, IsAdmin(), Command(commands=["admin"]))
@router.message(StartData.start, IsAdmin(), F.text == LEXICON["command_admin"])
async def cmd_admin(message: Message, state: FSMContext, session: AsyncSession):
    kb = get_admin_menu_kb()
    await message.answer(text=LEXICON["command_admin"], reply_markup=kb)


@router.callback_query(StartData.start, IsAdmin(), F.data == "admin_admins")
async def process_admin_btn(
    callback: CallbackQuery, state: FSMContext, session: AsyncSession
):
    await callback.message.answer(text="admins test")


@router.callback_query(StartData.start, IsAdmin(), F.data == "admin_lexicon")
async def process_lexicon_btn(
    callback: CallbackQuery, state: FSMContext, session: AsyncSession
):
    kb = get_lexicon_objs_kb()
    await callback.message.edit_text(text=LEXICON["lexicon_list"], reply_markup=kb)


@router.callback_query(
    StartData.start, IsAdmin(), LexiconCallbackFactory.filter(F.action == "return")
)
async def process_return_btn(
    callback: CallbackQuery, state: FSMContext, session: AsyncSession
):
    kb = get_admin_menu_kb()
    await callback.message.edit_text(text=LEXICON["command_admin"], reply_markup=kb)


@router.callback_query(
    StartData.start,
    IsAdmin(),
    F.data.startswith("lex"),
    LexiconCallbackFactory.filter(F.action == None),
)
async def process_lexicon_obj(
    callback: CallbackQuery,
    state: FSMContext,
    session: AsyncSession,
):
    lexicon_obj = LexiconCallbackFactory().unpack(callback.data)
    text = lexicon_obj.key + "\n\n" + LEXICON[lexicon_obj.key]
    btns = [
        [
            InlineKeyboardButton(
                text="Изменить ✏️",
                callback_data=LexiconCallbackFactory(action="change").pack(),
            ),
            InlineKeyboardButton(
                text=LEXICON["admin_return"],
                callback_data="admin_lexicon",
            ),
        ]
    ]
    kb = build_inline_kb(btns)
    await state.update_data(lexicon_key=lexicon_obj.key)
    await callback.message.edit_text(text=text, reply_markup=kb)


@router.callback_query(
    StartData.start,
    IsAdmin(),
    F.data.startswith("lex"),
    LexiconCallbackFactory.filter(F.action == "change"),
)
async def process_change_lexicon_obj(
    callback: CallbackQuery,
    state: FSMContext,
    session: AsyncSession,
):
    logger.info("change")
    await state.set_state(Lexicon.confirmation)
    await callback.message.edit_text(text="Введите новый текст объекта ✏️")


@router.message(
    Lexicon.confirmation,
    IsAdmin(),
)
async def process_fsm_lexicon_confirmation(
    message: Message,
    state: FSMContext,
    session: AsyncSession,
):
    await state.update_data(lexicon_text=message.text)
    state_data = await state.get_data()
    logger.info(state_data)
    btns = [
        [
            InlineKeyboardButton(
                text=LEXICON["confirm_lexicon"],
                callback_data=LexiconCallbackFactory(action="confirm").pack(),
            ),
            InlineKeyboardButton(
                text=LEXICON["cancel_lexicon"],
                callback_data=LexiconCallbackFactory(action="decline").pack(),
            ),
        ]
    ]
    kb = build_inline_kb(btns)
    await message.answer(text=f"Подтвердить изменение? {message.text}", reply_markup=kb)


@router.callback_query(
    Lexicon.confirmation,
    IsAdmin(),
    F.data.startswith("lex"),
    LexiconCallbackFactory.filter(F.action == "confirm"),
)
async def process_fsm_lexicon_confirm(
    callback: CallbackQuery,
    state: FSMContext,
    session: AsyncSession,
):
    state_data = await state.get_data()
    data = {
        "key": state_data["lexicon_key"],
        "text": LEXICON[state_data["lexicon_key"]],
    }

    logger.info(callback.message.text)
    logger.info(data)
    new_lex_obj = await update_lexicon_obj(
        session,
        data,
    )
    logger.info(new_lex_obj)
    await callback.message.answer(text="confirmed")
    # await message.answer(text="Пожалуйста, нажмите одну из кнопок!")


@router.callback_query(
    Lexicon.confirmation,
    IsAdmin(),
    F.data.startswith("lex"),
    LexiconCallbackFactory.filter(F.action == "decline"),
)
async def process_fsm_lexicon_decline(
    callback: CallbackQuery,
    state: FSMContext,
):
    kb = get_lexicon_objs_kb()
    await state.set_state(StartData.start)
    # state_data = await state.get_data()
    await callback.message.edit_text(text=LEXICON["lexicon_list"], reply_markup=kb)
