import codecs
import json
import os


_JSON_BYTE_ENCODINGS = {
    "utf-8", "utf-8-sig", "utf-16", "utf-16-le", "utf-16-be",
    "utf-32", "utf-32-le", "utf-32-be",
}


def api_key_from_environment():
    return os.getenv("SERP_API_KEY")


def _response_json(response):
    """Parse the JSON body of a requests or httpx2 response.

    httpx2 parses JSON from bytes without consulting the declared charset.
    Honor other text encodings before those bytes can be mistaken for UTF-8.
    """

    charset = getattr(response, "charset_encoding", None)
    if isinstance(charset, str) and charset:
        try:
            if codecs.lookup(charset).name not in _JSON_BYTE_ENCODINGS:
                return json.loads(response.content.decode(charset, errors="replace"))
        except LookupError:
            pass  # Unknown encoding or non-text codec; use the normal JSON decoder.

    try:
        return response.json()
    except UnicodeDecodeError:
        return json.loads(response.text)
