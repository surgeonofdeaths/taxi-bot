import requests
from loguru import logger
import os
from pprint import pprint

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

        if response.status_code == 200:
            logger.success("Request successful!")
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


def create_message(json: dict | None = None):
    url = build_url(URL, "messages")
    request = _request_url(url, HEADERS, method="post", json=json)
    return request


def get_customers():
    pass


if __name__ == "__main__":
    # pprint(get_message(1))
    json = {"chat": 1, "text": "A message from python code", "type": "message"}
    print(create_message(json))
