"""Run against SerpApi with API_KEY (or SERPAPI_KEY) set."""

import os
from urllib.parse import urlparse

import pytest

import serpapi


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
        {"url": "https://example.com/", "timeout": 30000},
        include_markdown=True,
        timeout=90,
    )

    assert_success(result)
    assert result["page_information"]["title"] == "Example Domain"
    assert result["page_information"]["final_url"] == "https://example.com/"
    assert isinstance(result["text_content"]["full"], str)
    assert result["text_content"]["full"].strip()
    assert isinstance(result["text_content"]["markdown"], str)
    assert result["text_content"]["markdown"].strip()


def test_live_extract_map(extract_live_client):
    result = extract_live_client.extract(
        url="https://www.python.org/",
        mode="map",
        include_sitemap=False,
        include_subdomains=False,
    )

    assert_success(result)
    urls = [entry["url"] for entry in result["urls"]]
    assert urls
    assert len(urls) == len(set(urls))
    assert all(urlparse(url).hostname == "www.python.org" for url in urls)
    assert all(urlparse(url).scheme in {"http", "https"} for url in urls)


def test_live_extract_crawl(extract_live_client):
    result = extract_live_client.extract(
        url="https://www.python.org/",
        mode="crawl",
        max_pages=2,
        max_depth=1,
    )

    assert_success(result)
    pages = result["pages"]
    assert len(pages) == 2
    assert pages[0]["url"] == "https://www.python.org/"
    assert pages[0]["depth"] == 0
    assert len({page["url"] for page in pages}) == 2
    for page in pages:
        assert "error" not in page
        assert page["text_content"]["full"]
        assert page["depth"] <= 1


@pytest.mark.parametrize("output", ["html", "md"])
def test_live_extract_text(extract_live_client, output):
    result = extract_live_client.extract(url="https://example.com/", output=output)

    assert isinstance(result, str)
    if output == "html":
        assert "<html" in result.lower()
        assert "</html>" in result.lower()
        assert "<title>Example Domain</title>" in result
        assert "<body" in result.lower()
        assert "</body>" in result.lower()
    else:
        assert result.startswith("---\n")
        metadata, separator, content = result[4:].partition("\n---\n")
        assert separator
        assert "search_metadata:" in metadata
        assert "engine: extract" in metadata
        assert content.strip()


def test_live_extract_markdown_only(extract_live_client):
    result = extract_live_client.extract(
        url="https://example.com/",
        include_markdown=True,
        json_restrictor="text_content.markdown",
    )

    assert isinstance(result, serpapi.SerpResults)
    assert set(result) == {"text_content"}
    assert set(result["text_content"]) == {"markdown"}
    assert isinstance(result["text_content"]["markdown"], str)
    assert result["text_content"]["markdown"].strip()


def test_live_extract_missing_url(extract_live_client):
    with pytest.raises(serpapi.HTTPError) as exc:
        extract_live_client.extract()

    assert exc.value.status_code == 400
    assert "url" in exc.value.error.lower()
