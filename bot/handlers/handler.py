from random import randint
from pprint import pprint
from aiogram import F, Router
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, KeyboardButton, Message, ReplyKeyboardMarkup
from aiogram.utils.keyboard import (
    InlineKeyboardBuilder,
    InlineKeyboardButton,
    ReplyKeyboardBuilder,
)
from aiogram.types.reply_keyboard_remove import ReplyKeyboardRemove
from keyboards.factory_kb import TestCallbackFactory
from keyboards.keyboard import get_keyboard_markup
from loguru import logger
from services import create_user
from sqlalchemy.ext.asyncio import AsyncSession
from utils.states.order_state import Order
from lexicon.lexicon import LEXICON, LEXICON_COMMANDS
from services.helpcrunch import create_message, search_customer
from services.db_service import get_user

router = Router()


@router.message(Command(commands=["start"]))
async def process_start_command(message: Message, session: AsyncSession):
    kb = [
        [KeyboardButton(text="Заказать такси")],
        [KeyboardButton(text="Связаться с оператором")],
        [KeyboardButton(text="О боте")],
    ]
    keyboard = ReplyKeyboardMarkup(keyboard=kb)
    await create_user(message.from_user, session)
    await message.answer(
        LEXICON_COMMANDS.get("start"),
        reply_markup=keyboard,
    )


@router.message(StateFilter(None), Command(commands=["order"]))
async def process_order_command(message: Message, state: FSMContext):
    button_contact = KeyboardButton(
        text=LEXICON.get("contact"),
        request_contact=True,
    )
    button_cancel = KeyboardButton(text=LEXICON.get("cancel"))
    keyboard = get_keyboard_markup(button_contact, button_cancel)

    await message.answer(
        LEXICON_COMMANDS.get("order"),
        reply_markup=keyboard,
    )
    await state.set_state(Order.getting_phone)


# TODO: more elegant way to cancel order
@router.message(Command(commands=["cancel"]))
@router.message(StateFilter("*"), F.text.lower() == "отменить заказ ❌")
async def process_fsm_cancel(message: Message, state: FSMContext):
    await state.clear()
    await message.answer(text="Заказ отменен", reply_markup=ReplyKeyboardRemove())


@router.message(Order.getting_phone)
async def process_fsm_phone(message: Message, state: FSMContext):
    # TODO: Should the bot allow others contacts?

    button_cancel = KeyboardButton(text=LEXICON.get("cancel"))
    if message.contact:

        keyboard = get_keyboard_markup(button_cancel)
        await state.update_data(phone_number=message.contact.phone_number)
        await state.set_state(Order.writing_start_address)
        await message.answer(
            text=LEXICON.get("get_start_address"),
            reply_markup=keyboard,
        )
    else:
        button_contact = KeyboardButton(
            text=LEXICON.get("contact"),
            request_contact=True,
        )

        keyboard = get_keyboard_markup(button_contact, button_cancel)
        await message.answer(
            text=LEXICON.get("contact_misspell"), reply_markup=keyboard
        )


@router.message(Order.writing_start_address)
async def process_fsm_start_address(message: Message, state: FSMContext):
    button_cancel = KeyboardButton(text=LEXICON.get("cancel"))
    keyboard = get_keyboard_markup(button_cancel)
    print(keyboard)
    await state.update_data(start_address=message.text)
    await state.set_state(Order.writing_destination_address)
    await message.answer(
        text=LEXICON.get("get_destination_address"), reply_markup=keyboard
    )


@router.message(Order.writing_destination_address)
async def process_fsm_destination_address(message: Message, state: FSMContext):
    button_cancel = KeyboardButton(text=LEXICON.get("cancel"))
    keyboard = get_keyboard_markup(button_cancel)
    await state.update_data(destination_address=message.text)
    await state.set_state(Order.writing_note)
    await message.answer(text=LEXICON.get("get_note"), reply_markup=keyboard)


@router.message(Order.writing_note)
async def process_fsm_note(message: Message, state: FSMContext, session: AsyncSession):
    await state.update_data(note=message.text)
    user_data = await state.get_data()
    text = f"Номер телефона: {user_data['phone_number']}\nНачальный адрес: {user_data['start_address']}\nАдрес прибытия: {user_data['destination_address']}\nПожелание: {user_data['note']}"

    user = await get_user(message.from_user.id, session)
    user.phone_number = user_data["phone_number"]
    await session.commit()

    chat_id = user.chat_id
    json = {"chat": chat_id, "text": text, "type": "message"}
    created_message = create_message(json)

    await state.clear()
    await message.answer(
        text=LEXICON.get("end_order"),
        reply_markup=ReplyKeyboardRemove(),
    )


@router.message()
async def process_wrong_text(message: Message):
    logger.info(f"User entered something else: {message.text}")
    await message.answer(LEXICON.get("user_misspell"))
