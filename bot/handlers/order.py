import asyncio

from aiogram import F, Router
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import KeyboardButton, Message
from db.models import User, Order as OrderModel
from filters.filter import validate_ukrainian_phone_number
from keyboards.keyboard import get_kb_markup, get_menu_kb
from lexicon.lexicon import LEXICON
from loguru import logger
from services.db_service import create_order, get_or_create, get_unprocessed_order
from services.helpcrunch import send_message
from services.other import get_order_info
from services.tasks import wait_for_operator
from sqlalchemy.ext.asyncio import AsyncSession, async_session
from states.state import Order, StartData

router = Router()


@router.message(
    StateFilter(
        Order.confirmation,
        Order.getting_phone,
        Order.writing_destination_address,
        Order.writing_start_address,
        Order.writing_note,
    ),
    F.text == LEXICON["stop_order"],
)
async def process_fsm_cancel(message: Message, state: FSMContext):
    state_data = await state.get_data()
    kb = get_menu_kb(
        has_order=state_data.get("has_order"),
        has_operator=state_data.get("has_operator"),
        is_admin=state_data.get("is_admin"),
    )

    await state.set_state(StartData.start)
    await message.answer(text=LEXICON.get("user_stop_order"), reply_markup=kb)


@router.message(StateFilter(Order.cancel_or_keep), F.text == LEXICON["cancel_order"])
async def process_fsm_cancel_order(
    message: Message, state: FSMContext, session: AsyncSession
):
    await state.update_data(has_order=False)
    state_data = await state.get_data()
    if state_data["unprocessed_order"]:
        order = await get_or_create(
            session, OrderModel, {"user_id": message.from_user.id}
        )
        await session.delete(order)
        await session.commit()
    kb = get_menu_kb(
        has_order=state_data.get("has_order"),
        has_operator=state_data.get("has_operator"),
        is_admin=state_data.get("is_admin"),
    )
    task = state_data.get("task_wait_for_operator")
    if task:
        task.cancel()

    chat_id = state_data["user"]["chat_id"]
    json = {
        "chat": chat_id,
        "text": LEXICON["send_operator_cancel_order"],
        "type": "message",
    }
    logger.info(json)
    notifier = send_message(json)
    logger.info(notifier)
    await state.set_state(StartData.start)
    await state.update_data(has_order=False)
    await message.answer(text=LEXICON["order_deleted"], reply_markup=kb)


@router.message(StateFilter(Order.cancel_or_keep), F.text == LEXICON["keep_order"])
async def process_fsm_keep_order(message: Message, state: FSMContext):
    state_data = await state.get_data()
    kb = get_menu_kb(
        has_order=True,
        has_operator=state_data.get("has_operator"),
        is_admin=state_data.get("is_admin"),
    )
    await state.update_data(has_order=True)
    await state.set_state(StartData.start)
    await message.answer(text=LEXICON["order_kept"], reply_markup=kb)


@router.message(StateFilter(Order.cancel_or_keep))
async def process_fsm_keep_order(
    message: Message, state: FSMContext, session: AsyncSession
):
    state_data = await state.get_data()
    buttons = [
        KeyboardButton(text=LEXICON["cancel_order"]),
        KeyboardButton(text=LEXICON["keep_order"]),
    ]
    kb = get_kb_markup(*buttons)
    order_obj = await get_or_create(
        session, OrderModel, {"user_id": message.from_user.id}
    )
    text = (
        LEXICON["has_order"] + "\n\n" + get_order_info(state_data, order_obj=order_obj)
    )

    await message.answer(
        text=text,
        reply_markup=kb,
    )


@router.message(Order.confirmation, Command(commands=["confirm"]))
@router.message(Order.confirmation, F.text == LEXICON["confirm"])
async def process_fsm_confirmation(
    message: Message, state: FSMContext, session: AsyncSession
):
    state_data = await state.get_data()
    text = get_order_info(state_data)
    logger.info(state_data)

    user = await session.get(User, message.from_user.id)
    user.phone_number = state_data["phone_number"]
    await session.commit()

    chat_id = user.chat_id
    json = {"chat": chat_id, "text": text, "type": "message"}
    logger.info(json)
    created_message = send_message(json)
    logger.info(created_message)

    await create_order(
        session,
        user_id=message.from_user.id,
        start_address=state_data["start_address"],
        destination_address=state_data["destination_address"],
        note=state_data.get("note"),
        message_id=created_message["id"],
    )

    kb = get_menu_kb(
        has_order=True,
        has_operator=state_data.get("has_operator"),
        is_admin=state_data.get("is_admin"),
    )

    if not state_data.get("has_operator"):
        task = asyncio.create_task(wait_for_operator(message, state, session))
        logger.info(task)
        await state.update_data(task_wait_for_operator=task)
    await state.set_state(StartData.start)
    await state.update_data(has_order=True)
    await message.answer(
        text=LEXICON.get("end_order"),
        reply_markup=kb,
    )


@router.message(Order.confirmation)
async def process_fsm_fail_confirmation(
    message: Message, state: FSMContext, session: AsyncSession
):
    button_cancel = KeyboardButton(text=LEXICON.get("stop_order"))
    button_confirm = KeyboardButton(text=LEXICON.get("confirm"))
    keyboard = get_kb_markup(button_confirm, button_cancel)

    await message.answer(
        text=LEXICON.get("fail_confirm"),
        reply_markup=keyboard,
    )


@router.message(StartData.start, Command(commands=["order"]))
@router.message(StartData.start, F.text == LEXICON["command_order"])
@router.message(StartData.start, F.text == LEXICON["command_my_order"])
async def process_order_command(
    message: Message, state: FSMContext, session: AsyncSession
):
    state_data = await state.get_data()
    logger.info(state_data)
    any_unprocessed_order = await get_unprocessed_order(message.from_user.id, session)
    user = await session.get(User, message.from_user.id)
    if any_unprocessed_order:
        buttons = [
            KeyboardButton(text=LEXICON["cancel_order"]),
            KeyboardButton(text=LEXICON["keep_order"]),
        ]
        kb = get_kb_markup(*buttons)

        text = (
            LEXICON["has_order"]
            + "\n\n"
            + get_order_info(order_obj=any_unprocessed_order)
        )
        await state.set_state(Order.cancel_or_keep)
        await state.update_data(unprocessed_order=True)
        await message.answer(
            text=text,
            reply_markup=kb,
        )
    elif user and user.phone_number:
        button_yes = KeyboardButton(text=LEXICON.get("btn_yes"))
        button_no = KeyboardButton(text=LEXICON.get("btn_no"))
        button_cancel = KeyboardButton(text=LEXICON.get("stop_order"))
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
        button_cancel = KeyboardButton(text=LEXICON.get("stop_order"))
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
    button_cancel = KeyboardButton(text=LEXICON.get("stop_order"))

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
    button_cancel = KeyboardButton(text=LEXICON.get("stop_order"))
    keyboard = get_kb_markup(button_cancel)
    await state.update_data(start_address=message.text)
    await state.set_state(Order.writing_destination_address)
    await message.answer(
        text=LEXICON.get("get_destination_address"), reply_markup=keyboard
    )


@router.message(Order.writing_destination_address)
async def process_fsm_destination_address(message: Message, state: FSMContext):
    btn_cancel = KeyboardButton(text=LEXICON.get("stop_order"))
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

    text = LEXICON["order_confirm"] + "\n\n" + get_order_info(user_data)
    button_cancel = KeyboardButton(text=LEXICON["stop_order"])
    button_confirm = KeyboardButton(text=LEXICON["confirm"])
    keyboard = get_kb_markup(button_confirm, button_cancel)

    await state.set_state(Order.confirmation)
    await message.answer(
        text=text,
        reply_markup=keyboard,
    )
