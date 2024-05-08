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

from lexicon.lexicon import LEXICON, LEXICON_COMMANDS
from aiogram.utils.keyboard import (
    InlineKeyboardMarkup,
    InlineKeyboardButton,
    InlineKeyboardBuilder,
    KeyboardButton,
    KeyboardBuilder,
    ReplyKeyboardMarkup,
    ReplyKeyboardBuilder,
)
from lexicon.lexicon import LEXICON

# from keyboards.factory_kb import TestCallbackFactory


def build_inline_kb(
    *buttons: tuple[KeyboardButton], adjust: int = 2
) -> InlineKeyboardBuilder:
    kb_builder = InlineKeyboardBuilder()
    kb_builder.row(*buttons)
    kb_builder.adjust(adjust)
    return kb_builder


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


def get_menu_kb(*extra_btns, has_order: bool = False, has_operator: bool = False):
    btns = []

    if has_order:
        order_btn = KeyboardButton(text=LEXICON_COMMANDS.get("my_order"))
    else:
        order_btn = KeyboardButton(text=LEXICON_COMMANDS.get("order"))
    btns.append(order_btn)

    if has_operator:
        contact_btn = KeyboardButton(text=LEXICON_COMMANDS.get("contact"))
        btns.append(contact_btn)

    if extra_btns:
        btns.extend(*extra_btns)
    btns.append(KeyboardButton(text=LEXICON_COMMANDS.get("help")))
    print(btns)
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
