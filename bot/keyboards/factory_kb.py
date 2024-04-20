from aiogram.filters.callback_data import CallbackData


class TestCallbackFactory(CallbackData, prefix="test"):
    name: str | None
