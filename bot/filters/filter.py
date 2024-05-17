import re

from aiogram import types
from aiogram.filters import BaseFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import Message
from config.config import settings
from loguru import logger


class IsAdmin(BaseFilter):
    def __init__(self, is_admin: bool | None = False):
        self.is_admin = is_admin

    async def __call__(
        self,
        message: Message,
        state: FSMContext,
    ) -> bool:
        if self.is_admin:
            return self.is_admin
        state_data = await state.get_data()
        user = state_data.get("user")
        self.is_admin = user.admin or self.is_admin
        return user.admin or self.is_admin


def validate_ukrainian_phone_number(phone_number: str) -> bool:
    pattern = r"^\+380\d{9}$"
    return re.match(pattern, phone_number)


def get_clean_username(username: str) -> str:
    if username.startswith("@"):
        username = username.lstrip("@")
    elif username.startswith("https://t.me/"):
        pattern = r"\/([^\/]+)$"
        match = re.search(pattern, username)
        if match:
            username = match.group(1)
    return username


if __name__ == "__main__":
    phone_number = "+380987654321"
    print(validate_ukrainian_phone_number(phone_number))
