import os
from unittest.mock import Mock
from urllib.parse import urlparse

import pytest
import requests

import serpapi


@pytest.fixture
def extract_request(monkeypatch):
    response = requests.Response()
    response.status_code = 200
    response.headers["Content-Type"] = "application/json"
    response._content = b'{"markdown": "Example content."}'
    request = Mock(return_value=response)
    monkeypatch.setattr(requests.Session, "request", request)
    return request


def test_extract_forwards_params_without_mutating_input(extract_request):
    client = serpapi.Client(api_key="client-key", timeout=60)
    params = {
        "url": "https://example.com/?q=coffee&lang=en",
        "engine": "google",
        "mode": "map",
        "include_markdown": False,
        "timeout": 30000,
    }
    original = params.copy()

    result = client.extract(params, engine="bing", mode="crawl", max_pages=2)

    assert params == original
    assert result["markdown"] == "Example content."
    extract_request.assert_called_once()
    _, sent = extract_request.call_args
    assert sent["method"] == "GET"
    assert sent["url"] == "https://serpapi.com/search"
    assert sent["params"] == dict(
        original, engine="extract", mode="crawl", max_pages=2, api_key="client-key"
    )
    assert sent["timeout"] == 60


def test_extract_separates_api_and_http_timeouts(extract_request):
    client = serpapi.Client(api_key="client-key", timeout=60)

    client.extract(
        {"url": "https://example.com/", "timeout": 30000},
        timeout=90,
    )

    _, sent = extract_request.call_args
    assert sent["params"]["timeout"] == 30000
    assert sent["timeout"] == 90


def test_module_extract_uses_request_key(extract_request):
    result = serpapi.extract(url="https://example.com/", api_key="request-key")

    assert result["markdown"] == "Example content."
    _, sent = extract_request.call_args
    assert sent["params"] == {
        "engine": "extract",
        "url": "https://example.com/",
        "api_key": "request-key",
    }


@pytest.fixture
def extract_live_client():
    api_key = os.environ.get("API_KEY") or os.environ.get("SERPAPI_KEY")
    if not api_key:
        pytest.fail("Extract API live tests require API_KEY or SERPAPI_KEY")
    client = serpapi.Client(api_key=api_key, timeout=180)
    yield client
    client.session.close()


def assert_success(result):
    assert isinstance(result, serpapi.SerpResults)
    assert "error" not in result
    assert result["search_metadata"]["status"] == "Success"


def test_live_extract_scrape(extract_live_client):
    result = extract_live_client.extract(
        {"url": "https://serpapi.com/", "timeout": 30000},
        timeout=90,
    )

    assert_success(result)
    assert "SerpApi" in result["page_information"]["title"]
    assert result["page_information"]["final_url"] == "https://serpapi.com/"
    assert isinstance(result["markdown"], str)
    assert result["markdown"].strip()


def test_live_extract_map(extract_live_client):
    result = extract_live_client.extract(
        url="https://serpapi.com/",
        mode="map",
        include_sitemap=False,
        include_subdomains=False,
    )

    assert_success(result)
    urls = [entry["url"] for entry in result["urls"]]
    assert urls
    assert len(urls) == len(set(urls))
    assert all(urlparse(url).hostname == "serpapi.com" for url in urls)
    assert all(urlparse(url).scheme in {"http", "https"} for url in urls)


def test_live_extract_crawl(extract_live_client):
    result = extract_live_client.extract(
        url="https://serpapi.com/",
        mode="crawl",
        max_pages=2,
        max_depth=1,
    )

    assert_success(result)
    pages = result["pages"]
    assert len(pages) == 2
    assert pages[0]["url"] == "https://serpapi.com/"
    assert pages[0]["depth"] == 0
    assert len({page["url"] for page in pages}) == 2
    for page in pages:
        assert "error" not in page
        assert page["markdown"]
        assert page["depth"] <= 1


@pytest.mark.parametrize("output", ["html", "md"])
def test_live_extract_text(extract_live_client, output):
    result = extract_live_client.extract(url="https://serpapi.com/", output=output)

    assert isinstance(result, str)
    assert "SerpApi" in result
    if output == "html":
        assert "<html" in result.lower()
        assert "</html>" in result.lower()
    else:
        assert "<html" not in result.lower()
        assert "search_metadata:" not in result


def test_live_extract_without_markdown(extract_live_client):
    result = extract_live_client.extract(url="https://serpapi.com/", include_markdown=False)
    assert_success(result)
    assert "SerpApi" in result["page_information"]["title"]
    assert "markdown" not in result
