from aiogram import F, Router
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import KeyboardButton, Message
from keyboards.keyboard import get_kb_markup, get_menu_kb
from loguru import logger
from sqlalchemy.ext.asyncio import AsyncSession
from states.state import Order
from lexicon.lexicon import LEXICON, LEXICON_COMMANDS
from services.helpcrunch import (
    send_message,
)
from services.other import wait_for_operator, get_order_info
from services.db_service import create_order, check_unprocessed_orders
from filters.filter import validate_ukrainian_phone_number
from db.models import User
import asyncio

router = Router()


# TODO: more elegant way to cancel order
@router.message(
    StateFilter(
        Order.confirmation,
        Order.getting_phone,
        Order.writing_destination_address,
        Order.writing_start_address,
        Order.writing_note,
    ),
    Command(commands=["cancel_order"]),
)
@router.message(F.text == LEXICON["cancel_order"])
async def process_fsm_cancel(message: Message, state: FSMContext):
    kb = get_menu_kb()
    await state.clear()
    await message.answer(text=LEXICON.get("user_cancel_order"), reply_markup=kb)


@router.message(Order.confirmation, Command(commands=["confirm"]))
@router.message(Order.confirmation, F.text == LEXICON["confirm"])
async def process_fsm_confirmation(
    message: Message, state: FSMContext, session: AsyncSession
):
    user_data = await state.get_data()
    text = get_order_info(user_data)
    logger.info(user_data)

    user = await session.get(User, message.from_user.id)
    user.phone_number = user_data["phone_number"]
    await session.commit()

    chat_id = user.chat_id
    json = {"chat": chat_id, "text": text, "type": "message"}
    logger.info(json)
    created_message = send_message(json)
    logger.info(created_message)

    await create_order(
        session,
        user_id=message.from_user.id,
        start_address=user_data["start_address"],
        destination_address=user_data["destination_address"],
        note=user_data.get("note"),
    )

    kb = get_menu_kb()

    # await state.set_state(Order.waiting_for_operator)
    await state.clear()
    asyncio.create_task(wait_for_operator(message, state, session))
    await message.answer(
        text=LEXICON.get("end_order"),
        reply_markup=kb,
    )


@router.message(Order.confirmation)
async def process_fsm_fail_confirmation(
    message: Message, state: FSMContext, session: AsyncSession
):
    button_cancel = KeyboardButton(text=LEXICON.get("cancel_order"))
    button_confirm = KeyboardButton(text=LEXICON.get("confirm"))
    keyboard = get_kb_markup(button_confirm, button_cancel)

    await message.answer(
        text=LEXICON.get("fail_confirm"),
        reply_markup=keyboard,
    )


@router.message(StateFilter(None), Command(commands=["order"]))
@router.message(StateFilter(None), F.text == LEXICON_COMMANDS["order"])
async def process_order_command(
    message: Message, state: FSMContext, session: AsyncSession
):
    any_unprocessed_order = await check_unprocessed_orders(
        message.from_user.id, session
    )
    user = await session.get(User, message.from_user.id)
    if any_unprocessed_order:
        print(any_unprocessed_order)
        buttons = [
            KeyboardButton(text=LEXICON["cancel_order"]),
        ]
        kb = get_kb_markup(*buttons)

        text = LEXICON["has_order"] + "\n\n" \
            + get_order_info(order_obj=any_unprocessed_order)
        await message.answer(
            text=text,
            reply_markup=kb,
        )
    elif user and user.phone_number:
        button_yes = KeyboardButton(text=LEXICON.get("btn_yes"))
        button_no = KeyboardButton(text=LEXICON.get("btn_no"))
        button_cancel = KeyboardButton(text=LEXICON.get("cancel_order"))
        keyboard = get_kb_markup(button_yes, button_no, button_cancel)

        await state.set_state(Order.getting_phone)
        await message.answer(
            LEXICON.get("has_contact") + f"\n\n{user.phone_number}",
            reply_markup=keyboard,
        )
    elif user:
        button_contact = KeyboardButton(
            text=LEXICON.get("share_contact"),
            request_contact=True,
        )
        button_cancel = KeyboardButton(text=LEXICON.get("cancel_order"))
        keyboard = get_kb_markup(button_contact, button_cancel)
        await message.answer(
            LEXICON.get("order"),
            reply_markup=keyboard,
        )
        await state.set_state(Order.getting_phone)
    else:
        logger.warning("No user in the database")
        kb = get_menu_kb()
        await message.answer(LEXICON.get("no_user"), reply_markup=kb)


@router.message(Order.getting_phone)
async def process_fsm_phone(message: Message, state: FSMContext, session: AsyncSession):
    # TODO: Should the bot allow others contacts?
    button_cancel = KeyboardButton(text=LEXICON.get("cancel_order"))

    if message.contact or message.text.lower().startswith("да"):
        keyboard = get_kb_markup(button_cancel)
        if message.contact:
            logger.info(message.contact.phone_number)
            await state.update_data(phone_number=message.contact.phone_number)
        else:
            user = await session.get(User, message.from_user.id)
            logger.info(user.phone_number)
            await state.update_data(phone_number=user.phone_number)
        await state.set_state(Order.writing_start_address)
        await message.answer(
            text=LEXICON.get("get_start_address"),
            reply_markup=keyboard,
        )
    elif message.text.lower().startswith("нет"):
        button_contact = KeyboardButton(
            text=LEXICON.get("share_contact"),
            request_contact=True,
        )

        keyboard = get_kb_markup(button_contact, button_cancel)
        await message.answer(text=LEXICON.get("order"), reply_markup=keyboard)
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
                text=LEXICON.get("share_contact"),
                request_contact=True,
            )

            keyboard = get_kb_markup(button_contact, button_cancel)
            await message.answer(
                text=LEXICON.get("contact_misspell"), reply_markup=keyboard
            )


@router.message(Order.writing_start_address)
async def process_fsm_start_address(message: Message, state: FSMContext):
    button_cancel = KeyboardButton(text=LEXICON.get("cancel_order"))
    keyboard = get_kb_markup(button_cancel)
    await state.update_data(start_address=message.text)
    await state.set_state(Order.writing_destination_address)
    await message.answer(
        text=LEXICON.get("get_destination_address"), reply_markup=keyboard
    )


@router.message(Order.writing_destination_address)
async def process_fsm_destination_address(message: Message, state: FSMContext):
    btn_cancel = KeyboardButton(text=LEXICON.get("cancel_order"))
    btn_no_note = KeyboardButton(text=LEXICON.get("no_note"))
    keyboard = get_kb_markup(btn_no_note, btn_cancel)
    await state.update_data(destination_address=message.text)
    await state.set_state(Order.writing_note)
    await message.answer(text=LEXICON.get("get_note"), reply_markup=keyboard)


@router.message(Order.writing_note)
async def process_fsm_note(
    message: Message,
    state: FSMContext,
    session: AsyncSession,
):
    if not message.text == LEXICON["no_note"]:
        await state.update_data(note=message.text)
    user_data = await state.get_data()

    text = LEXICON.get("order_confirm") + "\n\n" + get_order_info(user_data)
    button_cancel = KeyboardButton(text=LEXICON.get("cancel_order"))
    button_confirm = KeyboardButton(text=LEXICON.get("confirm"))
    keyboard = get_kb_markup(button_confirm, button_cancel)

    await state.set_state(Order.confirmation)
    await message.answer(
        text=text,
        reply_markup=keyboard,
    )
