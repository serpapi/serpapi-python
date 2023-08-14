import pytest

import serpapi


def test_basic_import():
    """Test that basic import works as intended."""
    import serpapi


def test_entrypoints(client):
    """Test that pure references to the publicly accessible API surface introduces no errors."""

    for api in [client, serpapi]:
        assert api.account
        assert api.search
        assert api.search_archive
        assert api.locations


def test_account_without_credentials():
    """Ensure that an HTTPError is raised when account is accessed without API Credentials."""
    with pytest.raises(serpapi.HTTPError):
        serpapi.account()


def test_account_with_bad_credentials(invalid_key_client):
    """Ensure that an HTTPError is raised when account is accessed with invalid API Credentials."""
    with pytest.raises(serpapi.HTTPError):
        invalid_key_client.account()


def test_account_with_credentials(client):
    """Ensure that account appears to be returning valid data if the API Key is correct."""
    account = client.account()
    assert account
    assert account.keys()
    assert isinstance(account, dict)


def test_coffee_search(coffee_search):
    assert isinstance(coffee_search, serpapi.SerpResults)
    assert hasattr(coffee_search, "__getitem__")


def test_coffee_search_as_dict(coffee_search):
    d = coffee_search.as_dict()
    assert isinstance(d, dict)


def test_coffee_search_html(coffee_search_html):
    assert isinstance(coffee_search_html, str)
    assert not hasattr(coffee_search_html, "next_page_url")


def test_coffee_search_n_pages(coffee_search):
    page_count = 0
    max_pages = 3

    for page in coffee_search.yield_pages(max_pages=max_pages):
        page_count += 1

    assert page_count == max_pages


def test_coffee_search_next_page(coffee_search):
    next_page = coffee_search.next_page()

    assert isinstance(next_page, serpapi.SerpResults)
    assert coffee_search["search_metadata"]["id"] != next_page["search_metadata"]["id"]


def test_search_function_signature(coffee_params, client):
    s = client.search(coffee_params)
    assert s["search_metadata"]["id"]

    s = client.search(**coffee_params)
    assert s["search_metadata"]["id"]

    s = client.search(q='coffee')
    assert s["search_metadata"]["id"]
