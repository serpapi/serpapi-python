import os


def api_key_from_environment():
    return os.getenv("SERP_API_KEY")
