import requests
from loguru import logger
import os
from pprint import pprint
from typing import Any

URL = "https://api.helpcrunch.com/v1"
BEARER_TOKEN = os.environ.get("BEARER_TOKEN")
HEADERS = {
    "Authorization": f"Bearer {BEARER_TOKEN}",
    "Content-Type": "application/json",
}


def build_url(*parts):
    return "/".join(s.strip("/") for s in parts)


def _request_by_method(url, headers, method: str = "get", json: dict | None = None):
    response = None

    if method.lower() == "get":
        response = requests.get(url, headers=headers)
    elif method.lower() == "post":
        response = requests.post(url, json=json, headers=headers)
    elif method.lower() == "patch":
        response = requests.patch(url, headers=headers, data=None)
    elif method.lower() == "put":
        response = requests.put(url, headers=headers, data=None)
    elif method.lower() == "delete":
        response = requests.delete(url, headers=headers)
    return response


def _request_url(url, headers, method: str = "get", json: dict | None = None) -> dict:
    try:
        response = _request_by_method(url, headers, method, json)

        if response.status_code in (200, 201):
            logger.success(f"Request successful! status code: {response.status_code}")
        else:
            logger.error(f"Request failed with status code: {response.status_code}")
        return response.json()
    except Exception as e:
        logger.error(f"An error occurred: {e}")


def get_message(chat_id: int, message_id: int | None = None) -> dict:
    url = build_url(URL, "chats", str(chat_id), "messages")

    request = _request_url(url, HEADERS, method="get")
    if not request.get("errors") and message_id:
        # TODO: get corresponding message by message_id
        pass
    return request


def send_message(message: dict):
    url = build_url(URL, "messages")
    request = _request_url(url, HEADERS, method="post", json=message)
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
    request = _request_url(url, HEADERS, method="post", json=filter)
    return request


def get_order_info(user_data: dict[str, Any]) -> str:
    note = f"\nПожелание: {user_data['note']}" if user_data.get('note') else ""
    text = f"Номер телефона: {user_data['phone_number']}\nНачальный адрес: {user_data['start_address']}\nАдрес прибытия: {user_data['destination_address']}" + note
    return text


def create_customer(user_id: str, name: str):
    body = {
        "userId": user_id,
        "name": name,
    }
    url = build_url(URL, "customers")
    request = _request_url(url, HEADERS, method="post", json=body)
    return request


def create_chat(customer_id: int, application: int = 2):
    body = {
        "customer": customer_id,
        "application": application,
    }
    url = build_url(URL, "chats")
    request = _request_url(url, HEADERS, method="post", json=body)
    return request


def get_customer(user_id: str):
    filter = {
        "filter": [
            {
                "field": "customers.userId",
                "operator": "=",
                "value": user_id
            }
        ],
        "limit": 1
    }
    url = build_url(URL, "customers", "search")
    request = _request_url(url, HEADERS, method="post", json=filter)
    return request


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
