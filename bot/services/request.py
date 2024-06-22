import requests
from loguru import logger


def build_url(*parts):
    return "/".join(s.strip("/") for s in parts)


def request_by_method(
    url, headers, method: str = "get", json: dict | None = None
) -> requests.Response:
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


def request_url(url, headers, method: str = "get", json: dict | None = None) -> dict:
    try:
        response = request_by_method(url, headers, method, json)

        if response.status_code in (200, 201):
            logger.success(f"Request successful! status code: {response.status_code}")
        else:
            logger.error(f"Request failed with status code: {response.status_code}")
        return response.json()
    except Exception as e:
        logger.error(f"An error occurred: {e}")
