from aiogram.filters.callback_data import CallbackData


class LexiconCallbackFactory(CallbackData, prefix="lex"):
    key: str | None = None
    action: str | None = None


class AdminCallbackFactory(CallbackData, prefix="admin"):
    username: str
    id: str
    action: str | None = None
