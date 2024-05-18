from aiogram.utils.keyboard import (InlineKeyboardBuilder,
                                    InlineKeyboardButton, InlineKeyboardMarkup,
                                    KeyboardBuilder, KeyboardButton,
                                    ReplyKeyboardBuilder, ReplyKeyboardMarkup)
from lexicon.lexicon import LEXICON
from loguru import logger
from sqlalchemy.ext.asyncio import AsyncSession

from bot.keyboards.factory_kb import (AdminCallbackFactory,
                                      LexiconCallbackFactory)
from bot.services.db_service import get_admin_users


def build_inline_kb(
    btns: list[InlineKeyboardButton], adjust: int | None = None
) -> InlineKeyboardMarkup | InlineKeyboardBuilder:
    if adjust:
        kb_builder = InlineKeyboardBuilder()
        kb_builder.row(*btns)
        kb_builder.adjust(adjust)
        return kb_builder
    keyboard = InlineKeyboardMarkup(inline_keyboard=btns)
    return keyboard


def build_kb(*buttons: tuple[KeyboardButton], adjust: int = 2) -> KeyboardBuilder:
    kb_builder = ReplyKeyboardBuilder()
    kb_builder.row(*buttons)
    kb_builder.adjust(adjust)
    return kb_builder


def get_kb_markup(
    *buttons: tuple[KeyboardButton], adjust: int = 2
) -> ReplyKeyboardMarkup:
    kb_markup = build_kb(*buttons, adjust=adjust)
    return kb_markup.as_markup(resize_keyboard=True)


def get_menu_kb(
    *extra_btns,
    has_order: bool = False,
    has_operator: bool = False,
    is_admin: bool = False,
):
    btns = []
    if has_order:
        order_type = "command_my_order"
    else:
        order_type = "command_order"

    btns.append(KeyboardButton(text=LEXICON.get(order_type)))

    if has_operator:
        btns.append(KeyboardButton(text=LEXICON["command_contact"]))
    if is_admin:
        btns.append(KeyboardButton(text=LEXICON["command_admin"]))
    if extra_btns:
        btns.extend(*extra_btns)
    btns.append(KeyboardButton(text=LEXICON.get("command_help")))
    kb = get_kb_markup(*btns)
    return kb


def get_admin_menu_kb() -> InlineKeyboardBuilder:
    btns = [
        [
            InlineKeyboardButton(
                text=LEXICON["admin_admins"], callback_data="get_admins"
            ),
            InlineKeyboardButton(
                text=LEXICON["admin_lexicon"], callback_data="get_lexicon"
            ),
        ]
    ]
    kb = build_inline_kb(btns)
    return kb


def get_lexicon_objs_kb() -> InlineKeyboardMarkup:
    btns = [
        InlineKeyboardButton(
            text=key,
            callback_data=LexiconCallbackFactory(key=key).pack(),
        )
        for key in LEXICON.keys()
    ]
    kb = build_inline_kb(btns, adjust=3)
    kb.row(
        InlineKeyboardButton(
            text=LEXICON["admin_return"],
            callback_data=LexiconCallbackFactory(action="return").pack(),
        )
    )
    kb = kb.as_markup(resize_keyboard=True)
    return kb


async def get_admins_kb(session: AsyncSession) -> InlineKeyboardMarkup:
    admins = await get_admin_users(session)
    logger.info(admins)
    btns = [
        InlineKeyboardButton(
            text=f"@{admin.username}",
            callback_data=AdminCallbackFactory(
                username=admin.username, id=str(admin.id)
            ).pack(),
        )
        for admin in admins
    ]
    kb = build_inline_kb(btns, adjust=2)
    kb.row(
        InlineKeyboardButton(
            text=LEXICON["admin_return"],
            callback_data=LexiconCallbackFactory(action="return").pack(),
        ),
        InlineKeyboardButton(
            text=LEXICON["admin_add"],
            callback_data="admin_add",
        ),
    )
    kb = kb.as_markup(resize_keyboard=True)
    return kb


# def form_buttons(*text: tuple[str]) -> list[KeyboardButton]:
#     KeyboardButton(text=t, )
#     buttons = [
#         KeyboardButton(
#             text=LEXICON.get("contact"),
#             request_contact=True,
#         )
#     ]
#     return buttons
