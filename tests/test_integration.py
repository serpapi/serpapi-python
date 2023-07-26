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
    with pytest.raises(serpapi.HTTPError):
        serpapi.account()


def test_account_with_bad_credentials(invalid_key_client):
    with pytest.raises(serpapi.HTTPError):
        invalid_key_client.account()


def test_account_with_credentials(client):
    assert client.account().keys()


def test_coffee_search(coffee_search):
    assert isinstance(coffee_search, serpapi.SerpResults)


def test_coffee_search_as_dict(coffee_search):
    d = coffee_search.as_dict()
    assert isinstance(d, dict)


def test_coffee_search_html(coffee_search_html):
    assert isinstance(coffee_search_html, str)


def test_coffee_search_n_pages(coffee_search):
    page_count = 0
    max_pages = 3

    for page in coffee_search.yield_pages(max_pages=max_pages):
        page_count += 1

    assert page_count == max_pages
