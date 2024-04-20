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
    InlineKeyboardMarkup,
    InlineKeyboardButton,
    InlineKeyboardBuilder,
    KeyboardButton,
    KeyboardBuilder,
    ReplyKeyboardMarkup,
)

# from keyboards.factory_kb import TestCallbackFactory


def build_inline_kb(*buttons: list[str], adjust: int = 2) -> InlineKeyboardBuilder:
    kb_builder = InlineKeyboardBuilder()
    kb_builder.row(*buttons)
    kb_builder.adjust(adjust)
    return kb_builder


def build_kb(*buttons: list[str]) -> KeyboardBuilder:
    print("build_kb")
    kb_builder = KeyboardBuilder(button_type=KeyboardButton)
    kb_builder.add(*buttons)
    return kb_builder


def get_keyboard_markup() -> ReplyKeyboardMarkup:
    button_contact = KeyboardButton(
        text="Отправить свой контакт ☎️",
        request_contact=True,
    )
    kb_markup = build_inline_kb(button_contact, adjust=2)
    return kb_markup.as_markup()
