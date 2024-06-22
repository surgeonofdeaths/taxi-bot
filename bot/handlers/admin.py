from aiogram import F, Router
from aiogram.filters import Command
from aiogram.filters.logic import or_f
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, InlineKeyboardButton, Message
from config.config import settings
from filters.filter import IsAdmin, get_clean_username
from keyboards.factory_kb import AdminCallbackFactory, LexiconCallbackFactory
from keyboards.keyboard import (
    build_inline_kb,
    get_admin_menu_kb,
    get_admins_kb,
    get_lexicon_objs_kb,
)
from lexicon.lexicon import LEXICON
from loguru import logger
from services.db_service import check_if_model_exists, get_or_create, update_lexicon_obj
from sqlalchemy.ext.asyncio import AsyncSession
from states.state import Admin, Lexicon, StartData

from bot.db.models import User

router = Router()


@router.message(
    StartData.start,
    IsAdmin(),
    or_f(Command(commands=["admin"]), F.text == LEXICON["command_admin"]),
)
async def cmd_admin(message: Message):
    kb = get_admin_menu_kb()
    await message.answer(text=LEXICON["command_admin"], reply_markup=kb)


@router.callback_query(StartData.start, IsAdmin(), F.data == "get_lexicon")
async def process_lexicon_btn(callback: CallbackQuery):
    kb = get_lexicon_objs_kb()
    await callback.message.edit_text(text=LEXICON["lexicon_list"], reply_markup=kb)


@router.callback_query(
    StartData.start, IsAdmin(), LexiconCallbackFactory.filter(F.action == "return")
)
async def process_return_btn(callback: CallbackQuery):
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
):
    logger.info(callback.data)
    logger.info(type(callback.data))
    lexicon_obj = LexiconCallbackFactory().unpack(callback.data)
    logger.info(lexicon_obj)
    text = f'<b>{lexicon_obj.key}</b>\n\n"{LEXICON[lexicon_obj.key]}"'

    btns = [
        [
            InlineKeyboardButton(
                text="Изменить ✏️",
                callback_data=LexiconCallbackFactory(action="change").pack(),
            ),
            InlineKeyboardButton(
                text=LEXICON["admin_return"],
                callback_data="get_lexicon",
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
):
    logger.info("change")
    state_data = await state.get_data()
    await state.set_state(Lexicon.confirmation)
    text = f'Введите новый текст объекта <b>"{state_data["lexicon_key"]}"</b> ✏️'
    await callback.message.edit_text(text=text)


@router.message(
    Lexicon.confirmation,
    IsAdmin(),
)
async def process_fsm_lexicon_confirmation(
    message: Message,
    state: FSMContext,
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
    state_data = await state.get_data()
    text = f'Подтвердить изменение объекта <b>{state_data["lexicon_key"]}</b>?\n\nСтарое значение:\n"{LEXICON[state_data["lexicon_key"]]}"\n\nНовое значение:\n"{message.text}"'
    await state.update_data(lexicon_text=message.text)
    await message.answer(text=text, reply_markup=kb)


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
        "text": state_data["lexicon_text"],
    }

    await update_lexicon_obj(
        session,
        data,
    )

    LEXICON[state_data["lexicon_key"]] = state_data["lexicon_text"]

    kb = get_lexicon_objs_kb()
    logger.info(LEXICON)
    text = f"Значение успешно измененно!\n{LEXICON['lexicon_list']}"
    await state.set_state(StartData.start)
    await callback.message.edit_text(text=text, reply_markup=kb)


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
    await callback.message.edit_text(text=LEXICON["lexicon_list"], reply_markup=kb)


@router.callback_query(StartData.start, IsAdmin(), F.data == "get_admins")
async def process_admin_btn(callback: CallbackQuery, session: AsyncSession):
    kb = await get_admins_kb(session)
    await callback.message.edit_text(text=LEXICON["admin_list"], reply_markup=kb)


@router.callback_query(StartData.start, IsAdmin(), F.data == "admin_add")
async def process_admin_add(
    callback: CallbackQuery,
    state: FSMContext,
):
    btns = [
        [
            InlineKeyboardButton(
                text=LEXICON["admin_cancel_adding"], callback_data="cancel_adding_user"
            ),
        ]
    ]
    kb = build_inline_kb(btns)
    await state.set_state(Admin.confirmation)
    await callback.message.edit_text(text=LEXICON["write_username"], reply_markup=kb)


@router.callback_query(Admin.confirmation, IsAdmin(), F.data == "cancel_adding_user")
@router.callback_query(StartData.start, IsAdmin(), F.data == "cancel_adding_user")
async def process_admin_adding_cancel(
    callback: CallbackQuery, state: FSMContext, session: AsyncSession
):
    kb = await get_admins_kb(session)
    await state.set_state(StartData.start)
    await callback.message.edit_text(text=LEXICON["admin_list"], reply_markup=kb)


@router.message(Admin.confirmation, IsAdmin())
async def process_admin_user(
    message: Message, state: FSMContext, session: AsyncSession
):
    username = message.text
    logger.info(username)
    username = get_clean_username(username)
    logger.info(username)
    user = await check_if_model_exists(session, User, {"username": username})
    logger.info(user)
    if user:
        text = f"@{username} успешно добавлен!"
        if user.admin:
            text = LEXICON["admin_user_exists"]
        else:
            user.admin = True
            await session.commit()
        kb = await get_admins_kb(session)
        await state.set_state(StartData.start)
        await message.answer(text=text, reply_markup=kb)
    else:
        btns = [
            [
                InlineKeyboardButton(
                    text="Отменить", callback_data="cancel_adding_user"
                ),
            ]
        ]
        kb = build_inline_kb(btns)
        await message.answer(text=LEXICON["no_username"], reply_markup=kb)
        logger.info("User does not exist")


@router.callback_query(
    StartData.start,
    IsAdmin(),
    F.data.startswith("admin"),
    AdminCallbackFactory.filter(F.username),
    AdminCallbackFactory.filter(~F.action),
)
async def process_admin_obj(
    query: CallbackQuery,
    callback_data: AdminCallbackFactory,
):
    btns = [
        [
            InlineKeyboardButton(
                text=LEXICON["admin_return"], callback_data="cancel_adding_user"
            ),
        ]
    ]
    if (
        callback_data.id != str(query.from_user.id)
        and int(callback_data.id) not in settings.bot.admin_ids
    ):
        btns[0].append(
            InlineKeyboardButton(
                text=LEXICON["admin_remove"],
                callback_data=AdminCallbackFactory(
                    username=callback_data.username,
                    id=callback_data.id,
                    action="admin_remove",
                ).pack(),
            )
        )
    kb = build_inline_kb(btns)
    text = f"Юзернейм пользователя: @{callback_data.username}\nID пользователя: {callback_data.id}"
    await query.message.edit_text(text=text, reply_markup=kb)


@router.callback_query(
    StartData.start,
    IsAdmin(),
    F.data.startswith("admin"),
    AdminCallbackFactory.filter(F.action == "admin_remove"),
)
async def process_admin_remove(
    query: CallbackQuery,
    callback_data: AdminCallbackFactory,
    session: AsyncSession,
):
    user = await get_or_create(
        session, User, {"id": int(callback_data.id), "username": callback_data.username}
    )
    user.admin = False
    await session.commit()
    logger.info(callback_data)
    kb = await get_admins_kb(session)
    text = f"@{callback_data.username} успешно удален!"
    await query.message.edit_text(text=text, reply_markup=kb)
