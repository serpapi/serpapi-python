"""Calls that must be rejected. Each `# type: ignore` must be needed (unused ignores fail the check)."""

from types import MappingProxyType
from typing import TYPE_CHECKING

import serpapi

if TYPE_CHECKING:
    from serpapi.engine_params import ExtractJsonParams, GoogleJsonSearchParams, SearchArchiveTextParams

client = serpapi.Client(api_key="secret")

client.search(engine="google", q="coffee", locaton="Austin")  # type: ignore
client.search(engine="gogle", q="coffee")  # type: ignore
client.search(search_query="coffee")  # type: ignore
client.search(engine="google", q="coffee", device="watch")  # type: ignore
# A Python bool is sent as "False", which SerpApi ignores here; the parameter takes "true" or "false".
client.search(engine="yandex", text="coffee", fix_typo=False)  # type: ignore
client.search(engine="google", q="coffee", output="xml")  # type: ignore
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
