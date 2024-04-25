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


def get_menu_kb():
    buttons = [
        KeyboardButton(text=LEXICON_COMMANDS.get("order")),
        KeyboardButton(text=LEXICON_COMMANDS.get("contact")),
        KeyboardButton(text=LEXICON_COMMANDS.get("help")),
    ]
    kb = get_kb_markup(*buttons)
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
