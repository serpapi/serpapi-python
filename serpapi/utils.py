import json
import os


def api_key_from_environment():
    return os.getenv("SERP_API_KEY")


def _response_json(response):
    """Parse the JSON body of a requests or httpx2 response.

    httpx2 only decodes UTF-8, UTF-16 and UTF-32 bodies. Like requests, decode
    any other body with the response's charset.
    """

    try:
        return response.json()
    except UnicodeDecodeError:
        return json.loads(response.text)
