from urllib.parse import parse_qs, urlparse

import pytest

import serpapi


def _query_param(url, param):
    values = parse_qs(urlparse(url).query).get(param)
    if values:
        return values[0]


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


def test_locations_query_limit_and_shape(client):
    locations = client.locations(q="Austin", limit=5)

    assert isinstance(locations, list)
    assert 0 < len(locations) <= 5

    expected_fields = {
        "id",
        "name",
        "canonical_name",
        "country_code",
        "target_type",
        "reach",
    }

    for location in locations:
        assert expected_fields.issubset(location.keys())
        assert isinstance(location["canonical_name"], str)

    assert any(
        "Austin" in location["name"] or "Austin" in location["canonical_name"]
        for location in locations
    )


def test_search_accepts_location_from_locations_api(client):
    locations = client.locations(q="Austin", limit=1)
    location_name = locations[0]["canonical_name"]

    search = client.search(q="coffee", location=location_name)

    assert search.get("error") is None
    assert search["organic_results"]
    assert "Austin" in search["search_parameters"]["location_requested"]
    assert "United States" in search["search_parameters"]["location_used"]


def test_account_without_credentials():
    """Ensure that an HTTPError is raised when account is accessed without API Credentials."""
    with pytest.raises(serpapi.HTTPError):
        serpapi.account()


def test_account_with_bad_credentials(invalid_key_client):
    """Ensure that an HTTPError is raised when account is accessed with invalid API Credentials."""
    with pytest.raises(serpapi.HTTPError) as exc_info:
        invalid_key_client.account()
        
    assert exc_info.value.response.status_code == 401


def test_account_with_credentials(client):
    """Ensure that account appears to be returning valid data if the API Key is correct."""
    account = client.account()
    assert account
    assert account.keys()
    assert isinstance(account, dict)


def test_search_with_missing_params(client):
    with pytest.raises(serpapi.HTTPError) as exc_info:
        client.search({ "q": "" })
        
    assert exc_info.value.status_code == 400
    assert "Missing query `q` parameter" in exc_info.value.error


def test_coffee_search(coffee_search):
    assert isinstance(coffee_search, serpapi.SerpResults)
    assert hasattr(coffee_search, "__getitem__")


def test_coffee_search_as_dict(coffee_search):
    d = coffee_search.as_dict()
    assert isinstance(d, dict)


def test_search_output_html_contains_raw_html_document(coffee_search_html):
    assert isinstance(coffee_search_html, str)
    assert "<html" in coffee_search_html.lower()
    assert "</html>" in coffee_search_html.lower()
    assert "coffee" in coffee_search_html.lower()
    assert not hasattr(coffee_search_html, "next_page_url")


def test_next_page_url_uses_serpapi_pagination_next(coffee_search):
    next_page_url = coffee_search.next_page_url

    assert next_page_url == coffee_search["serpapi_pagination"]["next"]
    assert _query_param(next_page_url, "start") == "10"
    assert _query_param(next_page_url, "api_key") is None


def test_yield_pages_returns_unique_search_pages(coffee_search):
    max_pages = 3
    pages = list(coffee_search.yield_pages(max_pages=max_pages))

    assert len(pages) == max_pages
    assert len({page["search_metadata"]["id"] for page in pages}) == max_pages
    assert "start" not in pages[0]["search_parameters"]
    assert int(pages[1]["search_parameters"]["start"]) == 10
    assert int(pages[2]["search_parameters"]["start"]) == 20


def test_next_page_advances_start_and_returns_new_results(coffee_search):
    next_page = coffee_search.next_page()

    assert isinstance(next_page, serpapi.SerpResults)
    assert coffee_search["search_metadata"]["id"] != next_page["search_metadata"]["id"]
    assert int(next_page["search_parameters"]["start"]) == 10
    assert next_page["organic_results"]

    page_number = next_page["search_information"].get("page_number")
    if page_number is not None:
        assert int(page_number) == 2


def test_search_archive_round_trips_search_id(client, coffee_search):
    search_id = coffee_search["search_metadata"]["id"]

    archived_search = client.search_archive(search_id=search_id)

    assert isinstance(archived_search, serpapi.SerpResults)
    assert archived_search["search_metadata"]["id"] == search_id


def test_search_function_signature(coffee_params, client):
    s = client.search(coffee_params)
    assert s["search_metadata"]["id"]

    s = client.search(**coffee_params)
    assert s["search_metadata"]["id"]

    s = client.search(q='coffee')
    assert s["search_metadata"]["id"]
