"""Checked with the SDK's optional async transport installed."""

import ssl
from pathlib import Path
from types import MappingProxyType
from typing import TYPE_CHECKING, Any, Dict, List, Mapping, Optional, Union

import httpx2
import requests
from typing_extensions import assert_type

import serpapi

if TYPE_CHECKING:
    from serpapi.engine_params import GoogleTextSearchParams, SearchArchiveParams, SearchParams


async def check_client(typed: "GoogleTextSearchParams", params: Mapping[str, Any]) -> None:
    async with serpapi.AsyncClient(api_key="secret", timeout=httpx2.Timeout(10)) as client:
        assert_type(client, serpapi.AsyncClient)
        result = await client.search(q="coffee", api_key=None, verify=ssl.create_default_context())
        assert_type(result, serpapi.AsyncSerpResults)
        assert_type(await client.search(engine="google", q="coffee", start=None, tbs=["a", "b"]), serpapi.AsyncSerpResults)
        proxies = MappingProxyType({"https": None})
        assert_type(await client.search(engine="google", q="coffee", proxies=proxies, verify=Path("ca.pem")), serpapi.AsyncSerpResults)
        assert_type(await client.search(typed, cert=(Path("cert.pem"), Path("key.pem"))), str)
        assert_type(await client.search(typed, output="json"), serpapi.AsyncSerpResults)
        assert_type(await client.search(params, output="md"), str)
        assert_type(await client.search_archive(params, output="json_with_pixel_position"), serpapi.AsyncSerpResults)
        assert_type(await client.extract(url="https://example.com", api_key=None, output="html"), str)
        assert_type(await client.search_archive(search_id="abc", api_key=None), serpapi.AsyncSerpResults)
        assert_type(await client.upload_image(Path("photo.jpg")), Dict[str, Any])
        assert_type(await client.locations(params), List[Dict[str, Any]])
        assert_type(await client.account(params), Dict[str, Any])
        assert_type(await result.next_page(), Optional[serpapi.AsyncSerpResults])
        async for page in result.yield_pages(max_pages=2):
            assert_type(page, serpapi.AsyncSerpResults)
            assert_type(page.as_dict(), Dict[str, Any])
        assert_type(client.session, httpx2.AsyncClient)
        response = await client.request("GET", "/search", params=params)
        assert_type(response, httpx2.Response)
        assert_type(serpapi.AsyncSerpResults.from_http_response(response, client=client), Union[serpapi.AsyncSerpResults, str])

        await client.search(engine="google", q="coffee", device="watch")  # type: ignore
        await client.search(engine="bing", q="coffee", output="json_with_pixel_position")  # type: ignore
        await client.search(q="coffee", timeout="30")  # type: ignore
        await client.extract()  # type: ignore
        await client.search_archive()  # type: ignore
        await result.yield_pages()  # type: ignore
    await client.aclose()


async def check_union_params(client: serpapi.AsyncClient, search: "SearchParams", archive: "SearchArchiveParams") -> None:
    assert_type(await client.search(search), Union[serpapi.AsyncSerpResults, Any])
    assert_type(await client.search_archive(archive), Union[serpapi.AsyncSerpResults, Any])


def check_response_transports(sync: requests.Response, async_: httpx2.Response) -> None:
    assert_type(serpapi.AsyncSerpResults.from_http_response(sync), Union[serpapi.AsyncSerpResults, str])
    assert_type(serpapi.SerpResults.from_http_response(async_), Union[serpapi.SerpResults, str])
