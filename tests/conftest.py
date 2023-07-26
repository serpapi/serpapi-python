import os

import pytest

import serpapi

os.environ["CI"] = "1"


@pytest.fixture
def api_key():
    return os.environ["API_KEY"]


@pytest.fixture
def client(api_key):
    return serpapi.Client(api_key=api_key)


@pytest.fixture
def invalid_key_client(api_key):
    return serpapi.Client(api_key="bunk-key")


@pytest.fixture
def coffee_params():
    return {"q": "Coffee"}


@pytest.fixture
def coffee_search(client, coffee_params):
    return client.search(**coffee_params)


@pytest.fixture
def coffee_search_html(client, coffee_params):
    params = coffee_params.copy()
    params["output"] = "html"

    return client.search(**params)
