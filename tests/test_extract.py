import json

import pytest
import requests

import serpapi
from serpapi.core import _client


@pytest.fixture
def extract_client():
    client = serpapi.Client(api_key="client-key", timeout=60)
    yield client
    client.session.close()


@pytest.fixture
def capture_request(monkeypatch, extract_client):
    calls = []

    def respond(status=200, payload=None, text=None):
        if payload is None:
            payload = {"page_information": {"title": "Example Domain"}}

        def request(**kwargs):
            calls.append(kwargs)
            response = requests.Response()
            response.status_code = status
            response.encoding = "utf-8"
            response._content = (
                text if text is not None else json.dumps(payload)
            ).encode("utf-8")
            return response

        monkeypatch.setattr(extract_client.session, "request", request)
        monkeypatch.setattr(_client.session, "request", request)
        return calls

    return respond


@pytest.mark.parametrize("entrypoint", ["client", "module"])
@pytest.mark.parametrize("style", ["dict", "kwargs", "mixed"])
def test_extract_public_calls(extract_client, capture_request, entrypoint, style):
    calls = capture_request()
    extract = extract_client.extract if entrypoint == "client" else serpapi.extract
    params = {"url": "https://example.com/", "api_key": "request-key"}
    original = params.copy()

    if style == "dict":
        result = extract(params)
    elif style == "kwargs":
        result = extract(**params)
    else:
        result = extract(params, include_markdown=True)

    assert isinstance(result, serpapi.SerpResults)
    assert result["page_information"]["title"] == "Example Domain"
    assert result.client is (extract_client if entrypoint == "client" else _client)
    assert params == original
    assert len(calls) == 1
    assert calls[0]["method"] == "GET"
    assert calls[0]["url"] == "https://serpapi.com/search"
    assert calls[0]["params"]["engine"] == "extract"
    assert calls[0]["params"]["api_key"] == "request-key"
    assert calls[0]["params"]["url"] == params["url"]
    if style == "mixed":
        assert calls[0]["params"]["include_markdown"] is True


def test_extract_overrides_engine_and_preserves_params(extract_client, capture_request):
    calls = capture_request()
    params = {"url": "https://example.com/", "engine": "google", "mode": "map"}
    original = params.copy()

    extract_client.extract(params, engine="bing", mode="scrape")

    assert params == original
    assert calls[0]["params"] == {
        "url": "https://example.com/",
        "engine": "extract",
        "mode": "scrape",
        "api_key": "client-key",
    }


@pytest.mark.parametrize("mode", ["scrape", "map", "crawl"])
def test_extract_forwards_api_options(extract_client, capture_request, mode):
    calls = capture_request()
    params = {
        "url": "https://example.com/?q=coffee&lang=en",
        "mode": mode,
        "max_pages": 2,
        "max_depth": 1,
        "include_subdomains": False,
        "include_sitemap": False,
        "include_markdown": True,
        "include_inline_assets": True,
        "include_tags": "main, article",
        "exclude_tags": "nav, footer",
        "prefetch_delay": 100,
        "timeout": 30000,
        "async": True,
        "device": "mobile",
        "zero_trace": True,
        "json_restrictor": "page_information,text_content",
    }
    original = params.copy()

    extract_client.extract(params)

    assert calls[0]["params"] == dict(original, engine="extract", api_key="client-key")
    assert calls[0]["timeout"] == 60
    assert params == original


def test_extract_separates_http_options(extract_client, capture_request):
    calls = capture_request()
    transport = {
        "timeout": (5, 90),
        "proxies": {"https": "http://proxy.example:8080"},
        "verify": "/tmp/ca.pem",
        "stream": True,
        "cert": ("/tmp/client.pem", "/tmp/client.key"),
    }
    extract_client.BASE_DOMAIN = "http://localhost:3000"

    extract_client.extract(
        {"url": "https://example.com/", "timeout": 30000}, **transport
    )

    assert calls[0]["url"] == "http://localhost:3000/search"
    assert calls[0]["params"]["timeout"] == 30000
    for name, value in transport.items():
        assert calls[0][name] == value
        if name != "timeout":
            assert name not in calls[0]["params"]


@pytest.mark.parametrize(
    "output, text",
    [("html", "<h1>Example Domain</h1>"), ("md", "# Example Domain\n\nCafé")],
    ids=["html", "md"],
)
def test_extract_text_outputs(extract_client, capture_request, output, text):
    calls = capture_request(text=text)

    result = extract_client.extract(url="https://example.com/", output=output)

    assert isinstance(result, str)
    assert result == text
    assert calls[0]["params"]["output"] == output


@pytest.mark.parametrize("status", [400, 401, 429, 500])
def test_extract_http_errors(extract_client, capture_request, status):
    capture_request(status=status, payload={"error": "Extract request failed"})

    with pytest.raises(serpapi.HTTPError) as exc:
        extract_client.extract(url="https://example.com/")

    assert exc.value.status_code == status
    assert exc.value.error == "Extract request failed"


@pytest.mark.parametrize(
    "cause, expected",
    [
        (requests.exceptions.Timeout, serpapi.TimeoutError),
        (requests.exceptions.ConnectionError, serpapi.HTTPConnectionError),
    ],
)
def test_extract_transport_errors(monkeypatch, extract_client, cause, expected):
    def fail(**kwargs):
        raise cause("Request failed")

    monkeypatch.setattr(extract_client.session, "request", fail)

    with pytest.raises(expected):
        extract_client.extract(url="https://example.com/")


def test_extract_preserves_json_error_response(extract_client, capture_request):
    capture_request(payload={"error": "Failed to fetch target page"})

    result = extract_client.extract(url="https://example.com/")

    assert isinstance(result, serpapi.SerpResults)
    assert result["error"] == "Failed to fetch target page"


def test_search_still_selects_requested_engine(extract_client, capture_request):
    calls = capture_request()

    extract_client.extract(url="https://example.com/")
    extract_client.search(engine="bing", q="coffee")

    assert calls[0]["params"]["engine"] == "extract"
    assert calls[1]["params"]["engine"] == "bing"
    assert "url" not in calls[1]["params"]
