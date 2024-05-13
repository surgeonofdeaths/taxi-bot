# from aiogram.utils.keyboard import (
#     InlineKeyboardBuilder,
#     InlineKeyboardButton,
#     InlineKeyboardMarkup,
# )

# from keyboards.factory_kb import NavigationCallbackFactory
# from lexicon.lexicon import LEXICON
# from services import megacmd, other

# from subprocess import CalledProcessError


# def build_inline_kb(*buttons: list[str]) -> InlineKeyboardMarkup:

#     kb_builder = InlineKeyboardBuilder()
#     kb_builder.row(*buttons)
#     kb_builder.adjust(3)
#     return kb_builder.as_markup()

# from keyboards.factory_kb import NavigationCallbackFactory

from aiogram.utils.keyboard import (
    InlineKeyboardBuilder,
    KeyboardBuilder,
    KeyboardButton,
    ReplyKeyboardBuilder,
    ReplyKeyboardMarkup,
)
from lexicon.lexicon import LEXICON

# from keyboards.factory_kb import TestCallbackFactory


def build_inline_kb(
    *buttons: tuple[KeyboardButton], adjust: int = 2
) -> InlineKeyboardBuilder:
    kb_builder = InlineKeyboardBuilder()
    kb_builder.row(*buttons)
    kb_builder.adjust(adjust)
    return kb_builder.as_markup(resize_keyboard=True)


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
    is_admin: bool = False
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


# def form_buttons(*text: tuple[str]) -> list[KeyboardButton]:
#     KeyboardButton(text=t, )
#     buttons = [
#         KeyboardButton(
#             text=LEXICON.get("contact"),
#             request_contact=True,
#         )
#     ]
#     return buttons
