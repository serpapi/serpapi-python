"""Calls that must be rejected. Each `# type: ignore` must be needed (unused ignores fail the check)."""

from types import MappingProxyType
from typing import TYPE_CHECKING, Any, Dict, Union

import serpapi

if TYPE_CHECKING:
    from serpapi.engine_params import (
        BingJsonSearchParams, ExtractJsonParams, GoogleJsonSearchParams, GoogleTextSearchParams,
        SearchArchiveJsonParams, SearchArchiveTextParams, SearchParams,
    )

client = serpapi.Client(api_key="secret")

client.search(engine="google", q="coffee", locaton="Austin")  # type: ignore
client.search(engine="gogle", q="coffee")  # type: ignore
client.search(search_query="coffee")  # type: ignore
client.search(engine="google", q="coffee", device="watch")  # type: ignore
client.search(engine="google", q="coffee", device=["mobile"])  # type: ignore
client.extract(url=None)  # type: ignore
# A Python bool is sent as "False", which SerpApi ignores here; the parameter takes "true" or "false".
client.search(engine="yandex", text="coffee", fix_typo=False)  # type: ignore
client.search(engine="google", q="coffee", output="xml")  # type: ignore
client.search(engine="bing", q="coffee", output="json_with_pixel_position")  # type: ignore
client.search(engine="google", q="coffee", timeout="30")  # type: ignore
client.search(engine="google", q="coffee", proxies=MappingProxyType({"https": "http://proxy:8080"}))  # type: ignore
serpapi.extract()  # type: ignore
client.search_archive()  # type: ignore
serpapi.Client("secret")  # type: ignore
serpapi.upload_image(123)  # type: ignore

# search() and search_archive() write the API key into the mapping they receive.
client.search(MappingProxyType({"engine": "google", "q": "coffee"}))  # type: ignore
client.search_archive(MappingProxyType({"search_id": "abc"}))  # type: ignore

# Untyped dict literals match the fallback overload unchecked; annotate them with a TypedDict for key checking.
typo: "GoogleJsonSearchParams" = {"engine": "google", "qq": "coffee"}  # type: ignore
bad_output: "GoogleJsonSearchParams" = {"engine": "google", "q": "coffee", "output": "md"}  # type: ignore
no_url: "ExtractJsonParams" = {"timeout": 30000}  # type: ignore
no_search_id: "SearchArchiveTextParams" = {"output": "md"}  # type: ignore


def incompatible_outputs(
    text: "GoogleTextSearchParams", json: "GoogleJsonSearchParams", bing: "BingJsonSearchParams",
    archive_text: "SearchArchiveTextParams", archive_json: "SearchArchiveJsonParams", unknown: "SearchParams",
) -> None:
    client.search(text, output="json")  # type: ignore
    serpapi.search(json, start=10, output="md")  # type: ignore
    client.search(bing, output="json_with_pixel_position")  # type: ignore
    client.search_archive(archive_json, output="html")  # type: ignore
    serpapi.search_archive(archive_text, output="json")  # type: ignore
    client.search(unknown, output="md")  # type: ignore
    client.search(unknown, timeout="30")  # type: ignore


def unsafe_overrides(params: "Union[SearchParams, Dict[str, Any]]", text: "GoogleTextSearchParams", options: Dict[str, int]) -> None:
    serpapi.search(params, output="json")  # type: ignore
    client.search(text, **options)  # type: ignore
