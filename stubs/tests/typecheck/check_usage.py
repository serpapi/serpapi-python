"""Calls that must type-check, with their expected types."""

from types import MappingProxyType
from typing import TYPE_CHECKING, Any, Dict, List, Union

from typing_extensions import TypedDict, assert_type

import serpapi
from serpapi import Client, SerpResults

if TYPE_CHECKING:
    from serpapi.engine_params import (
        ExtractTextParams,
        GoogleJsonSearchParams,
        GoogleTextSearchParams,
        SearchArchiveParams,
        SearchArchiveTextParams,
        SearchParams,
    )

client = Client(api_key="secret", timeout=20)

assert_type(client.search(engine="google", q="coffee"), SerpResults)
assert_type(client.search(q="coffee", location=None, start=None, tbs=("a", "b")), SerpResults)
assert_type(client.search(q="coffee", location="Austin, Texas", no_cache=True), SerpResults)
assert_type(client.search(engine="bing", q="coffee", output="html"), str)
assert_type(client.search(engine="bing", q="coffee", mkt="en-US", cc="us", safeSearch="Moderate"), SerpResults)
assert_type(client.search(engine="tripadvisor_reviews", place_id="g60763", type_of_visit="Business,Couples"), SerpResults)
assert_type(client.search(engine="yahoo_shopping", p="tv", min_price=100), SerpResults)
assert_type(client.search(engine="home_depot", q="chair", store_id=2118), SerpResults)
assert_type(client.search(engine="google_lens", image_id="abc", hl="en"), SerpResults)
assert_type(client.search(engine="google", q="coffee", timeout=(3.0, 30.0), verify=False), SerpResults)
assert_type(client.search(engine="google", q="coffee", proxies=None, cert=None, verify=None, stream=None), SerpResults)
assert_type(client.search(engine="google", q="coffee", proxies={"https": None}), SerpResults)
proxy_urls: Dict[str, str] = {"https": "http://proxy:8080"}
optional_proxy_urls: Dict[str, Union[str, None]] = {"https": None}
assert_type(client.search(engine="google", q="coffee", proxies=proxy_urls), SerpResults)
assert_type(client.search(engine="google", q="coffee", proxies=optional_proxy_urls), SerpResults)
assert_type(client.search(engine="ebay", _nkw="coffee", _blrs="spell_auto_correct"), SerpResults)
assert_type(client.search(engine="google_maps", q="coffee", min_rating=4.5), SerpResults)
assert_type(client.search(engine="doordash", q="coffee", min_rating=4.5), SerpResults)
assert_type(client.search(engine="amazon", k="coffee", language="en_US"), SerpResults)
assert_type(client.search(engine="naver", query="coffee", page=2, start=21), SerpResults)
assert_type(client.search(engine="yandex", text="coffee", sort_mode="date"), SerpResults)
assert_type(client.search({"engine": "google", "q": "coffee", "async": True}), SerpResults)
client.search({"engine": "google_images", "tbm": "isch", "q": "coffee"})
client.search({"engine": "google_play", "q": "kite", "store": "apps", "max_results": "2"})
assert_type(client.search({"engine": "google", "q": "coffee", "output": "md"}), str)
assert_type(client.search({"engine": "google_translate", "text": "hi", "from": "en"}), SerpResults)
assert_type(serpapi.search(engine="google", q="coffee", output="md"), str)
# Pixel Position is documented for Google, Google Ads, and the Search Archive.
assert_type(client.search(engine="google", q="coffee", output="json_with_pixel_position"), SerpResults)
assert_type(client.search(engine="google_ads", q="coffee", output="json_with_pixel_position"), SerpResults)
assert_type(client.search({"engine": "google", "q": "coffee", "output": "json_with_pixel_position"}), SerpResults)
assert_type(client.search_archive(search_id="abc", output="json_with_pixel_position"), SerpResults)
# Documented values that the Playground's option list leaves out.
assert_type(client.search(engine="walmart", query="coffee", sort="new"), SerpResults)
assert_type(client.search(engine="youtube_channel", channel_id="abc", hl="en-gb"), SerpResults)

def runtime_engine(name: str) -> None:
    assert_type(client.search({"engine": name, "q": "coffee"}), Union[SerpResults, Any])

params: Dict[str, Any] = {"engine": "google", "q": "coffee"}
assert_type(client.search(params), Union[SerpResults, Any])
assert_type(client.search(params, start=10), Union[SerpResults, Any])
# An `output` keyword overrides the mapping, so the result type is known even for an untyped dict.
assert_type(client.search(params, output="md"), str)
assert_type(client.extract({"url": "https://example.com"}, output="html"), str)
assert_type(client.search(params, output="json"), SerpResults)
assert_type(client.extract(params, output="json"), SerpResults)
assert_type(client.search_archive(params, output="json"), SerpResults)


def mapping_output_overrides(
    search: "GoogleTextSearchParams", extract: "ExtractTextParams", archive: "SearchArchiveTextParams"
) -> None:
    assert_type(client.search(search, output="html", start=10), str)
    assert_type(client.search(dict(search), output="json"), SerpResults)
    assert_type(client.extract(extract, output="json"), SerpResults)
    assert_type(client.search_archive(archive, output="md"), str)
    assert_type(serpapi.search_archive(dict(archive), output="json"), SerpResults)

typed: "GoogleJsonSearchParams" = {"engine": "google", "q": "coffee", "device": None, "api_key": None, "tbs": ["a", "b"]}
assert_type(client.search(typed), SerpResults)
assert_type(client.search(typed, start=10), SerpResults)
assert_type(serpapi.search(typed, output="json_with_pixel_position"), SerpResults)


# Function parameters keep their declared union; a module-level assignment would be narrowed.
def any_engine(params: "SearchParams", archive: "SearchArchiveParams") -> None:
    assert_type(client.search(params), Union[SerpResults, str])
    assert_type(serpapi.search(params, start=10), Union[SerpResults, str])
    assert_type(client.search_archive(archive), Union[SerpResults, str])
    assert_type(client.search(dict(params), output="json"), SerpResults)
    assert_type(serpapi.search(dict(params), output="md"), str)
    assert_type(client.search(dict(params), start=10), Union[SerpResults, Any])


def typed_or_raw(params: "Union[SearchParams, Dict[str, Any]]") -> None:
    assert_type(client.search(params), Union[SerpResults, Any])
    assert_type(serpapi.search(params, start=10), Union[SerpResults, Any])


class StartOption(TypedDict):
    start: int


def known_overrides(params: "GoogleJsonSearchParams", options: StartOption) -> None:
    assert_type(client.search(params, **options), SerpResults)


assert_type(client.extract(url="https://example.com"), SerpResults)
assert_type(client.extract(MappingProxyType({"url": "https://example.com"})), Union[SerpResults, Any])
assert_type(client.extract({"url": "https://example.com", "timeout": 30000, "output": "md"}), str)
assert_type(serpapi.search_archive(search_id="abc"), SerpResults)
assert_type(client.search_archive({"search_id": "abc", "output": "html"}), str)

results = client.search(q="coffee")
assert_type(results.next_page_url, Union[str, None])
assert_type(results.next_page(), Union[SerpResults, str, None])
for page in results.yield_pages(max_pages=2):
    assert_type(page, Union[SerpResults, str])
    if isinstance(page, str):
        break
    assert_type(page.as_dict(), Dict[str, Any])
assert_type(results.as_dict(), Dict[str, Any])

assert_type(client.upload_image("photo.jpg"), Dict[str, Any])
assert_type(serpapi.locations(q="Austin", limit=3), List[Dict[str, Any]])
assert_type(serpapi.account(), Dict[str, Any])

try:
    client.search(q="coffee")
except serpapi.HTTPError as error:
    assert_type(error.status_code, int)
    assert_type(error.error, Union[str, None])
