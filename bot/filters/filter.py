import re

from aiogram import types
from aiogram.filters import BaseFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import Message
from config.config import settings
from db.database import sessionmaker
from loguru import logger
from sqlalchemy.ext.asyncio import AsyncSession

from bot.db.models import User
from bot.services.db_service import check_if_model_exists, get_or_create


class IsAdmin(BaseFilter):
    def __init__(self, is_admin: bool | None = False):
        self.is_admin = is_admin

    async def __call__(
        self,
        message: Message,
        state: FSMContext,
    ) -> bool:
        # TODO: remove admin work

        async with sessionmaker() as session:
            user = await get_or_create(
                session,
                User,
                {
                    "id": message.from_user.id,
                    "username": message.from_user.username,
                    "first_name": message.from_user.first_name,
                    "last_name": message.from_user.last_name,
                },
            )
            user_data = {
                "is_admin": user.admin,
                "chat_id": user.chat_id,
                "customer_id": user.customer_id,
            }
            logger.info(user_data)
            await state.update_data(user=user_data)
        self.is_admin = user.admin
        return self.is_admin


class HasUser(BaseFilter):
    def __init__(self, has_user: bool | None = False):
        self.has_user = has_user

    async def __call__(
        self,
        message: Message,
        session: AsyncSession,
    ) -> bool:
        exists = check_if_model_exists(session, User, {"id": message.from_user.id})
        self.has_user = exists
        return exists


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


async def check_admin(session: AsyncSession, message: Message, user_data: dict) -> bool:
    logger.info(user_data)
    if not user_data.get("is_admin"):
        admin_ids = settings.bot.admin_ids
        user = await get_or_create(
            session,
            User,
            {
                "id": message.from_user.id,
                "username": message.from_user.username,
                "first_name": message.from_user.first_name,
                "last_name": message.from_user.last_name,
            },
        )
        if not user.admin:
            user.admin = message.from_user.id in admin_ids
        await session.commit()
        return user.admin
    else:
        return user_data["is_admin"]


if __name__ == "__main__":
    phone_number = "+380987654321"
    print(validate_ukrainian_phone_number(phone_number))
