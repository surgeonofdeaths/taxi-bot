from aiogram.types import Message
from config.config import settings
from loguru import logger
from sqlalchemy.ext.asyncio import AsyncSession

from bot.db.models import User
from bot.filters.filter import check_admin
from bot.services.db_service import get_or_create

from .request import build_url, request_url

URL = "https://api.helpcrunch.com/v1"
BEARER_TOKEN = settings.helpcrunch.bearer_token
HEADERS = {
    "Authorization": f"Bearer {BEARER_TOKEN}",
    "Content-Type": "application/json",
}


def get_messages(chat_id: int) -> dict:
    url = build_url(URL, "chats", str(chat_id), "messages")

    request = request_url(url, HEADERS, method="get")
    messages = request.get("data")
    return messages


def send_message(message: dict):
    url = build_url(URL, "messages")
    request = request_url(url, HEADERS, method="post", json=message)

    return request


def search_customer(telegram_id: str | int):
    filter = {
        "filter": [
            {
                "field": "customers.userId",
                "operator": "=",
                "value": telegram_id,
            }
        ],
        "limit": 1,
        "order": "DESC",
    }
    url = build_url(URL, "customers", "search")
    request = request_url(url, HEADERS, method="post", json=filter)
    return request


def create_customer(user_id: str, name: str):
    body = {
        "userId": user_id,
        "name": name,
    }
    url = build_url(URL, "customers")
    request = request_url(url, HEADERS, method="post", json=body)
    return request


def create_chat(customer_id: int, application: int = 1):
    body = {
        "customer": customer_id,
        "application": application,
    }
    logger.info(body)
    url = build_url(URL, "chats")
    request = request_url(url, HEADERS, method="post", json=body)
    return request


def get_or_create_chat(user_id: str, customer_id: int, application: int = 1):
    chat = search_chat(user_id)
    if not chat["data"]:
        chat = create_chat(customer_id, application)
        logger.info(chat)
    else:
        chat = chat["data"][0]
        logger.info(chat)
    return chat


def get_customer(user_id: str):
    filter = {
        "filter": [{"field": "customers.userId", "operator": "=", "value": user_id}],
        "limit": 1,
    }
    url = build_url(URL, "customers", "search")
    request = request_url(url, HEADERS, method="post", json=filter)
    return request


def search_chat(user_id: str):
    filter = {
        "filter": [
            {"field": "chats.customer.userId", "operator": "=", "value": user_id}
        ],
        "sort": "chats.createdAt",
        "order": "desc",
        "offset": 0,
        "limit": 100,
    }
    url = build_url(URL, "chats", "search")
    request = request_url(url, HEADERS, method="post", json=filter)
    return request


def get_assignee(chat: dict):
    try:
        assignee = chat["data"][0]["assignee"]
        return assignee
    except KeyError as e:
        return e


async def get_user_state(
    message: Message,
    session: AsyncSession,
    user_dict: dict | None = None,
):

    if user_dict is None:
        user_dict = {}
    is_admin = await check_admin(session, message, user_dict)
    user_dict["is_admin"] = is_admin
    if not user_dict.get("customer_id"):
        customer = get_customer(message.from_user.id)
        logger.info(customer)
        if customer and not customer.get("data"):
            customer = create_customer(
                message.from_user.id, message.from_user.full_name
            )
            logger.info(customer)
            customer_id = customer["id"]
        else:
            logger.info(customer)
            customer_id = customer["data"][0]["id"]
        chat = get_or_create_chat(message.from_user.id, customer_id)
        logger.info(chat)
        chat_id = chat["id"]

        filter = get_user_filter(
            user=message.from_user,
            chat_id=chat_id,
            customer_id=customer_id,
        )
        logger.info(filter)
        user = await get_or_create(
            session,
            User,
            filter,
        )
        logger.info(user)
        user.chat_id = str(chat_id)
        user.customer_id = str(customer_id)
        await session.commit()

        user_dict["chat_id"] = chat_id
        user_dict["customer_id"] = customer_id
    return user_dict


def get_user_filter(**kwargs) -> dict:
    user = kwargs["user"]
    username = user.username if user.username else "no_username"
    filter = {}
    filter["id"] = user.id
    filter["username"] = username
    filter["first_name"] = user.first_name
    filter["last_name"] = user.last_name
    return filter


if __name__ == "__main__":
    # pprint(get_message(1))
    # customer = search_customer("1013857410")
    # print(customer)
    # chat_id = customer["data"][0]["id"]
    # json = {"chat": chat_id, "text": "A message from python code", "type": "message"}
    # print(send_messagk(json))
    # customer = create_customer("1013857410", "Artem")
    customer = get_customer("1013857410")
    logger.info(customer)
