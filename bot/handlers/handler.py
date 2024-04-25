from random import randint
from pprint import pprint
from aiogram import F, Router
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import default_state
from aiogram.types import CallbackQuery, KeyboardButton, Message, ReplyKeyboardMarkup
from aiogram.utils.keyboard import (
    InlineKeyboardBuilder,
    InlineKeyboardButton,
    ReplyKeyboardBuilder,
)
from aiogram.types.reply_keyboard_remove import ReplyKeyboardRemove
from keyboards.factory_kb import TestCallbackFactory
from keyboards.keyboard import get_kb_markup, get_menu_kb
from loguru import logger
from services import create_user
from sqlalchemy.ext.asyncio import AsyncSession
from states.order_state import Order
from lexicon.lexicon import LEXICON, LEXICON_COMMANDS
from services.helpcrunch import send_message, search_customer, get_order_info
from services.db_service import get_user
from filters.filter import validate_ukrainian_phone_number

router = Router()


@router.message(Command(commands=["start"]))
async def process_start_command(message: Message, session: AsyncSession):
    kb = get_menu_kb()
    await create_user(message.from_user, session)
    await message.answer(
        LEXICON_COMMANDS.get("start"),
        reply_markup=kb,
    )


# TODO: more elegant way to cancel order
@router.message(
    StateFilter(
        Order.confirmation,
        Order.getting_phone,
        Order.writing_destination_address,
        Order.writing_start_address,
        Order.writing_note,
    ),
    Command(commands=["cancel"]),
)
@router.message(F.text.lower() == "отменить заказ ❌")
async def process_fsm_cancel(message: Message, state: FSMContext):
    kb = get_menu_kb()
    await state.clear()
    await message.answer(text=LEXICON.get("user_cancel_order"), reply_markup=kb)


@router.message(Order.confirmation, Command(commands=["confirm"]))
@router.message(Order.confirmation, F.text.lower() == "подтвердить заказ ✅")
async def process_fsm_confirmation(
    message: Message, state: FSMContext, session: AsyncSession
):
    user_data = await state.get_data()
    text = get_order_info(user_data)
    logger.info(user_data["note"])

    user = await get_user(message.from_user.id, session)
    user.phone_number = user_data["phone_number"]
    await session.commit()

    chat_id = user.chat_id
    json = {"chat": chat_id, "text": text, "type": "message"}
    created_message = send_message(json)
    kb = get_menu_kb()

    await state.clear()
    await message.answer(
        text=LEXICON.get("end_order"),
        reply_markup=kb,
    )


@router.message(Order.confirmation)
async def process_fsm_fail_confirmation(
    message: Message, state: FSMContext, session: AsyncSession
):
    button_cancel = KeyboardButton(text=LEXICON.get("cancel"))
    button_confirm = KeyboardButton(text=LEXICON.get("confirm"))
    keyboard = get_kb_markup(button_confirm, button_cancel)

    await message.answer(
        text=LEXICON.get("fail_confirm"),
        reply_markup=keyboard,
    )


@router.message(StateFilter(None), Command(commands=["help"]))
@router.message(StateFilter(None), F.text.lower() == "информация о боте")
async def cmd_help(message: Message, state: FSMContext, session: AsyncSession):
    await message.answer(
        text=LEXICON_COMMANDS.get("help"),
    )


@router.message(StateFilter(None), Command(commands=["order"]))
@router.message(StateFilter(None), F.text.lower() == "заказать такси")
async def process_order_command(
    message: Message, state: FSMContext, session: AsyncSession
):
    user = await get_user(message.from_user.id, session)
    logger.info(user)
    if user and user.phone_number:
        button_yes = KeyboardButton(text="Да, использовать")
        button_no = KeyboardButton(text="Нет, ввести новый")
        button_cancel = KeyboardButton(text=LEXICON.get("cancel"))
        keyboard = get_kb_markup(button_yes, button_no, button_cancel)

        await state.set_state(Order.getting_phone)
        await message.answer(
            LEXICON.get("has_contact") + f"\n\n{user.phone_number}",
            reply_markup=keyboard,
        )
    else:
        button_contact = KeyboardButton(
            text=LEXICON.get("contact"),
            request_contact=True,
        )
        button_cancel = KeyboardButton(text=LEXICON.get("cancel"))
        keyboard = get_kb_markup(button_contact, button_cancel)
        await message.answer(
            LEXICON.get("order"),
            reply_markup=keyboard,
        )
        await state.set_state(Order.getting_phone)


@router.message(Order.getting_phone)
async def process_fsm_phone(message: Message, state: FSMContext, session: AsyncSession):
    # TODO: Should the bot allow others contacts?

    button_cancel = KeyboardButton(text=LEXICON.get("cancel"))

    if message.contact or message.text.lower().startswith("да"):
        keyboard = get_kb_markup(button_cancel)
        if message.contact:
            await state.update_data(phone_number=message.contact.phone_number)
        else:
            user = await get_user(message.from_user.id, session)
            await state.update_data(phone_number=user.phone_number)
        await state.set_state(Order.writing_start_address)
        await message.answer(
            text=LEXICON.get("get_start_address"),
            reply_markup=keyboard,
        )
    elif message.text.lower().startswith("нет"):
        button_contact = KeyboardButton(
            text=LEXICON.get("contact"),
            request_contact=True,
        )

        keyboard = get_kb_markup(button_contact, button_cancel)
        await message.answer(text=LEXICON_COMMANDS.get("order"), reply_markup=keyboard)
    else:
        is_valid = validate_ukrainian_phone_number(message.text.strip())
        if is_valid:
            keyboard = get_kb_markup(button_cancel)
            await state.update_data(phone_number=message.text.strip())
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

            keyboard = get_kb_markup(button_contact, button_cancel)
            await message.answer(
                text=LEXICON.get("contact_misspell"), reply_markup=keyboard
            )


@router.message(Order.writing_start_address)
async def process_fsm_start_address(message: Message, state: FSMContext):
    button_cancel = KeyboardButton(text=LEXICON.get("cancel"))
    keyboard = get_kb_markup(button_cancel)
    await state.update_data(start_address=message.text)
    await state.set_state(Order.writing_destination_address)
    await message.answer(
        text=LEXICON.get("get_destination_address"), reply_markup=keyboard
    )


@router.message(Order.writing_destination_address)
async def process_fsm_destination_address(message: Message, state: FSMContext):
    button_cancel = KeyboardButton(text=LEXICON.get("cancel"))
    keyboard = get_kb_markup(button_cancel)
    await state.update_data(destination_address=message.text)
    await state.set_state(Order.writing_note)
    await message.answer(text=LEXICON.get("get_note"), reply_markup=keyboard)


@router.message(Order.writing_note)
async def process_fsm_note(message: Message, state: FSMContext, session: AsyncSession):
    await state.update_data(note=message.text)
    user_data = await state.get_data()

    text = LEXICON.get("order_confirm") + "\n\n" + get_order_info(user_data)
    button_cancel = KeyboardButton(text=LEXICON.get("cancel"))
    button_confirm = KeyboardButton(text=LEXICON.get("confirm"))
    keyboard = get_kb_markup(button_confirm, button_cancel)

    await state.set_state(Order.confirmation)
    await message.answer(
        text=text,
        reply_markup=keyboard,
    )


@router.message()
async def process_wrong_text(message: Message):
    logger.info(f"User entered something else: {message.text}")
    await message.answer(LEXICON.get("user_misspell"))
