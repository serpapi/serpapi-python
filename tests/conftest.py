import os

import pytest

import serpapi

os.environ["CI"] = "1"


def pytest_addoption(parser):
    parser.addoption(
        "--require-docs-key",
        action="store_true",
        help="Fail instead of skipping live docs examples when the API key is missing",
    )


def pytest_sessionstart(session):
    if session.config.getoption("--require-docs-key") and not (
        os.environ.get("SERPAPI_KEY") or os.environ.get("API_KEY")
    ):
        raise pytest.UsageError("Live docs checks require SERPAPI_KEY or API_KEY")


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
