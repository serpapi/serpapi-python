import asyncio
from io import BytesIO
from urllib.parse import parse_qs

import httpx
import pytest

import serpapi


def run(coroutine):
    return asyncio.run(coroutine)


async def replace_session(client, handler):
    await client.session.aclose()
    client.session = httpx.AsyncClient(
        transport=httpx.MockTransport(handler),
        follow_redirects=True,
        timeout=None,
    )


def test_module_exposes_async_client():
    assert serpapi.AsyncClient

    async def exercise():
        client = serpapi.AsyncClient()
        try:
            assert repr(client) == "<SerpApi AsyncClient>"
        finally:
            await client.aclose()

    run(exercise())


def test_async_client_endpoints_and_context_manager():
    requests = []

    async def handler(request):
        requests.append(request)
        path = request.url.path
        if path == "/search":
            return httpx.Response(
                200,
                headers={"Content-Type": "application/json"},
                json={"search_metadata": {"id": "search-123"}},
            )
        if path == "/searches/search-123":
            return httpx.Response(200, json={"search_metadata": {"id": "search-123"}})
        if path == "/account.json":
            return httpx.Response(200, json={"account_id": "account-123"})
        if path == "/locations.json":
            return httpx.Response(200, json=[{"name": "Austin"}])
        if path == "/image":
            return httpx.Response(200, json={"image_id": "image-123"})
        raise AssertionError(f"Unexpected path: {path}")

    async def exercise():
        client = serpapi.AsyncClient(api_key="test-key", timeout=12)
        await replace_session(client, handler)
        session = client.session
        async with client:
            search = await client.search(engine="google", q="coffee")
            archive = await client.search_archive(search_id="search-123")
            account = await client.account()
            locations = await client.locations(q="Austin", limit=1)
            image = BytesIO(b"fake-image")
            upload = await client.upload_image(image, zero_trace="true")
            assert not image.closed
        return search, archive, account, locations, upload, session

    search, archive, account, locations, upload, session = run(exercise())

    assert isinstance(search, serpapi.AsyncSerpResults)
    assert search["search_metadata"]["id"] == "search-123"
    assert archive["search_metadata"]["id"] == "search-123"
    assert account == {"account_id": "account-123"}
    assert locations == [{"name": "Austin"}]
    assert upload == {"image_id": "image-123"}
    assert session.is_closed
    assert len(requests) == 5

    search_query = parse_qs(requests[0].url.query.decode())
    assert search_query == {
        "engine": ["google"],
        "q": ["coffee"],
        "api_key": ["test-key"],
    }
    assert requests[0].headers["User-Agent"].startswith("serpapi-python")
    assert b"fake-image" in requests[-1].content
    assert b"zero_trace" in requests[-1].content


def test_async_search_supports_text_output():
    async def handler(request):
        return httpx.Response(
            200,
            headers={"Content-Type": "text/markdown; charset=utf-8"},
            text="# Coffee",
        )

    async def exercise():
        client = serpapi.AsyncClient(api_key="test-key")
        await replace_session(client, handler)
        async with client:
            return await client.search(engine="google", q="coffee", output="md")

    assert run(exercise()) == "# Coffee"


def test_async_pagination_fetches_only_requested_pages():
    requested_pages = []

    async def handler(request):
        start = int(request.url.params.get("start", 0))
        requested_pages.append(start)
        page = start // 10 + 1
        data = {"search_information": {"page_number": page}}
        if page < 3:
            data["serpapi_pagination"] = {
                "next": f"https://serpapi.com/search?start={start + 10}"
            }
        return httpx.Response(
            200,
            headers={"Content-Type": "application/json"},
            json=data,
        )

    async def exercise():
        client = serpapi.AsyncClient(api_key="test-key")
        await replace_session(client, handler)
        async with client:
            first = await client.search(engine="google", q="coffee")
            pages = [page async for page in first.yield_pages(max_pages=2)]
            return pages

    pages = run(exercise())
    assert [page["search_information"]["page_number"] for page in pages] == [1, 2]
    assert all(isinstance(page, serpapi.AsyncSerpResults) for page in pages)
    assert requested_pages == [0, 10]


def test_async_client_runs_requests_concurrently_on_one_session():
    in_flight = 0
    max_in_flight = 0

    async def handler(request):
        nonlocal in_flight, max_in_flight
        in_flight += 1
        max_in_flight = max(max_in_flight, in_flight)
        await asyncio.sleep(0.02)
        in_flight -= 1
        return httpx.Response(200, json={"query": request.url.params["q"]})

    async def exercise():
        client = serpapi.AsyncClient(api_key="test-key")
        await replace_session(client, handler)
        session = client.session
        async with client:
            results = await asyncio.gather(
                client.search(q="coffee"),
                client.search(q="tea"),
                client.search(q="pizza"),
            )
            assert client.session is session
        return results

    results = run(exercise())
    assert [result["query"] for result in results] == ["coffee", "tea", "pizza"]
    assert max_in_flight == 3


@pytest.mark.parametrize(
    ("transport_error", "expected_error"),
    [
        (httpx.ConnectError("connection failed"), serpapi.HTTPConnectionError),
        (httpx.ReadTimeout("request timed out"), serpapi.TimeoutError),
    ],
)
def test_async_client_translates_transport_errors(transport_error, expected_error):
    async def handler(request):
        transport_error.request = request
        raise transport_error

    async def exercise():
        client = serpapi.AsyncClient(api_key="test-key")
        await replace_session(client, handler)
        async with client:
            with pytest.raises(expected_error) as failure:
                await client.search(q="coffee")
            assert failure.value.__cause__ is transport_error

    run(exercise())


def test_async_client_preserves_http_error_details():
    async def handler(request):
        return httpx.Response(401, json={"error": "Invalid API key"})

    async def exercise():
        client = serpapi.AsyncClient(api_key="bad-key")
        await replace_session(client, handler)
        async with client:
            with pytest.raises(serpapi.HTTPError) as failure:
                await client.account()
            assert failure.value.status_code == 401
            assert failure.value.error == "Invalid API key"
            assert failure.value.request.url.path == "/account.json"
            assert failure.value.response.status_code == 401

    run(exercise())


def test_async_archive_requires_search_id_before_request():
    async def exercise():
        client = serpapi.AsyncClient(api_key="test-key")
        try:
            with pytest.raises(serpapi.SearchIDNotProvided):
                await client.search_archive()
        finally:
            await client.aclose()

    run(exercise())


def test_async_requests_style_options_use_scoped_client(monkeypatch):
    created = []

    class ScopedAsyncClient:
        def __init__(self, **options):
            self.options = options
            created.append(self)

        async def __aenter__(self):
            return self

        async def __aexit__(self, exc_type, exc_value, traceback):
            for transport in self.options.get("mounts", {}).values():
                if transport is not None:
                    await transport.aclose()

        async def request(self, **kwargs):
            self.request_kwargs = kwargs
            request = httpx.Request(kwargs["method"], kwargs["url"])
            return httpx.Response(200, json={"ok": True}, request=request)

    async def exercise():
        client = serpapi.AsyncClient(api_key="test-key")
        monkeypatch.setattr(httpx, "AsyncClient", ScopedAsyncClient)
        try:
            return await client.search(
                q="coffee",
                proxies={"https": "http://proxy.example.com:8080"},
                verify=False,
                stream=True,
            )
        finally:
            await client.aclose()

    assert run(exercise()) == {"ok": True}
    assert len(created) == 1
    assert created[0].options["verify"] is False
    assert "https://" in created[0].options["mounts"]
    assert "stream" not in created[0].request_kwargs
