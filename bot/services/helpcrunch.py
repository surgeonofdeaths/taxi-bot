import requests
from loguru import logger
import os

URL = "https://api.helpcrunch.com/v1"
BEARER_TOKEN = os.environ.get("BEARER_TOKEN")

headers = {
    "Authorization": f"Bearer {BEARER_TOKEN}",
    "Content-Type": "application/json",
}


def build_url(*parts):
    return "/".join(s.strip("/") for s in parts)


def request_by_method(url, headers, method="GET"):
    response = None

    if method.lower() == "get":
        response = requests.get(url, headers=headers)
    elif method.lower() == "post":
        response = requests.post(url, headers=headers)
    elif method.lower() == "patch":
        response = requests.patch(url, headers=headers, data=None)
    elif method.lower() == "put":
        response = requests.put(url, headers=headers, data=None)
    elif method.lower() == "delete":
        response = requests.delete(url, headers=headers)
    return response


def request_url(url, headers, method="get"):
    try:
        response = request_by_method(url, headers, method)

        if response.status_code == 200:
            logger.success("Request successful!")
            return response.json()
        else:
            logger.error(f"Request failed with status code: {response.status_code}")
            return response.text

    except Exception as e:
        logger.info(f"An error occurred: {e}")


def get_all_messages(chat_id):
    url = build_url(URL, "chats", str(chat_id), "messages")
    print(request_url(url, headers, method="get"))


get_all_messages(1)
