from aiogram.filters.callback_data import CallbackData


class LexiconCallbackFactory(CallbackData, prefix="lex"):
    key: str | None
