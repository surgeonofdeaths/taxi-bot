# from pprint import pprint

from loguru import logger
from .request import build_url, request_url

# from db.models import Order
from config.config import settings

URL = "https://api.helpcrunch.com/v1"
BEARER_TOKEN = settings.helpcrunch.bearer_token
HEADERS = {
    "Authorization": f"Bearer {BEARER_TOKEN}",
    "Content-Type": "application/json",
}


def get_message(chat_id: int, message_id: int | None = None) -> dict:
    url = build_url(URL, "chats", str(chat_id), "messages")

    request = request_url(url, HEADERS, method="get")
    message = request["data"][0][0]
    return message
    # if not request.get("errors") and message_id:
    #     # latest
    # return request


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


def create_chat(customer_id: int, application: int = 2):
    body = {
        "customer": customer_id,
        "application": application,
    }
    url = build_url(URL, "chats")
    request = request_url(url, HEADERS, method="post", json=body)
    return request


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
