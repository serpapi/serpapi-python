import asyncio
import io
import json
import logging
import pickle
import ssl
import threading
from collections import UserDict
from pathlib import Path

import certifi
import pytest
import requests

# AsyncClient needs the async extra, which is only available on Python 3.11 and later.
httpx2 = pytest.importorskip("httpx2")

import serpapi  # noqa: E402
from serpapi.http import _select_proxy, _ssl_context  # noqa: E402

pytestmark = pytest.mark.anyio


@pytest.fixture
def anyio_backend():
    return "asyncio"


@pytest.fixture(autouse=True)
def clean_transport_environment(monkeypatch):
    for name in ("http_proxy", "https_proxy", "all_proxy", "no_proxy"):
        monkeypatch.delenv(name, raising=False)
        monkeypatch.delenv(name.upper(), raising=False)
    for name in ("REQUESTS_CA_BUNDLE", "CURL_CA_BUNDLE", "SSL_CERT_FILE", "SSL_CERT_DIR"):
        monkeypatch.delenv(name, raising=False)


class Server:
    """Answers requests and records which pool actually sent each one."""

    def __init__(self):
        self.handler = lambda request: httpx2.Response(200, json={})
        self.requests = []
        self.pools = []
        self.sent_via = []

    async def handle(self, request):
        self.requests.append(request)
        response = self.handler(request)
        if asyncio.iscoroutine(response):
            response = await response
        return response

    @property
    def last_request(self):
        return self.requests[-1]


@pytest.fixture
def server(monkeypatch):
    server = Server()

    class Pool(httpx2.MockTransport):
        def __init__(self, **options):
            super().__init__(server.handle)
            self.proxy = options["proxy"]
            self.is_closed = False
            server.pools.append((options, self))

        async def handle_async_request(self, request):
            server.sent_via.append(self.proxy)
            return await super().handle_async_request(request)

        async def aclose(self):
            self.is_closed = True

    monkeypatch.setattr(httpx2, "AsyncHTTPTransport", Pool)
    return server


@pytest.fixture
async def async_client(server):
    async with serpapi.AsyncClient(api_key="test-api-key") as client:
        yield client


async def test_search_sends_the_same_request_as_client(async_client, server):
    results = await async_client.search(
        engine="google", q="coffee shops", no_cache=True, start=None, tbs=["a", "b"]
    )

    assert isinstance(results, serpapi.AsyncSerpResults)
    assert results.client is async_client
    assert str(server.last_request.url) == (
        "https://serpapi.com/search"
        "?engine=google&q=coffee+shops&no_cache=True&tbs=a&tbs=b&api_key=test-api-key"
    )
    assert server.last_request.headers["User-Agent"] == serpapi.HTTPClient.USER_AGENT


@pytest.mark.parametrize("constructor,overrides,keys", [
    (None, {}, ["session"]),
    ("constructor", {}, ["constructor"]),
    ("constructor", {"api_key": "per-call"}, ["per-call"]),
    ("constructor", {"api_key": None}, []),
])
async def test_search_merges_session_defaults(server, constructor, overrides, keys):
    async with serpapi.AsyncClient(api_key=constructor) as client:
        client.session.params = {"api_key": "session", "hl": "en", "gl": "us", "start": 10}
        await client.search(engine="google", q="coffee", gl="ca", start=None, **overrides)
        query = server.last_request.url.params
        assert (query.get("engine"), query.get("q"), query.get("hl"), query.get("gl")) == (
            "google", "coffee", "en", "ca"
        )
        assert "start" not in query
        assert query.get_list("api_key") == keys
        assert client.session.params["gl"] == "us"


async def test_session_defaults_preserve_existing_query_bytes(server):
    raw = "q=iced%20tea&flag&x=1&z=2&x=3"
    server.handler = lambda request: httpx2.Response(
        200, json={"serpapi_pagination": {"next": "https://serpapi.com/search?" + raw}}
    )
    async with serpapi.AsyncClient() as client:
        client.session.params = {
            "q": "default", "x": "default", "flag": "default",
            "tag": ["a", "b"], "api_key": "session",
        }
        result = await client.search(q="first")
        await result.next_page()
    assert server.last_request.url.query.startswith(raw.encode("ascii") + b"&")
    query = server.last_request.url.params
    assert query.get_list("q") == ["iced tea"] and query.get_list("x") == ["1", "3"]
    assert query.get_list("flag") == [""] and query.get_list("tag") == ["a", "b"]
    assert query.get_list("api_key") == ["session"]


@pytest.mark.parametrize(
    "overrides,keys", [({}, ["session"]), ({"api_key": "form"}, []), ({"api_key": None}, [])]
)
async def test_upload_session_key_does_not_compete_with_form_key(server, overrides, keys):
    async with serpapi.AsyncClient() as client:
        client.session.params = {"api_key": "session"}
        await client.upload_image(io.BytesIO(b"image"), **overrides)
    assert server.last_request.url.params.get_list("api_key") == keys
    assert (b'name="api_key"' in server.last_request.content) == (overrides.get("api_key") == "form")


@pytest.mark.parametrize("data", [
    UserDict({"api_key": "form", "tag": ["one", "two"]}),
    [("tag", "one"), (b"api_key", "form"), ("tag", "two")],
])
async def test_multipart_form_key_suppresses_query_defaults(async_client, server, data):
    async_client.session.params = {"api_key": "session"}
    await async_client.request("POST", "/image", {}, data=data, files={"image": b"image"})
    assert "api_key" not in server.last_request.url.params
    body = server.last_request.content
    assert b'name="api_key"\r\n\r\nform' in body
    assert body.index(b'name="tag"\r\n\r\none') < body.index(b'name="tag"\r\n\r\ntwo')


@pytest.mark.parametrize("value,expected", [(None, []), ("per-call", ["per-call"])])
async def test_bytes_query_names_override_text_defaults(async_client, server, value, expected):
    async_client.session.params = {"api_key": "session", "hl": "en"}
    await async_client.search({b"api_key": value, b"hl": None})
    assert server.last_request.url.params.get_list("api_key") == expected
    assert "hl" not in server.last_request.url.params


@pytest.mark.parametrize("method", ["search", "search_archive", "locations", "account"])
async def test_shared_params_do_not_carry_over_between_calls(async_client, server, method):
    base = {"search_id": "original"}
    async with serpapi.AsyncClient(api_key="second-key") as other:
        await asyncio.gather(*(getattr(async_client, method)(base, gl=gl) for gl in ("us", "ca")))
        await getattr(other, method)(base)

    assert base == {"search_id": "original"}
    assert [(r.url.params.get("gl"), r.url.params["api_key"]) for r in server.requests] == [
        ("us", "test-api-key"), ("ca", "test-api-key"), (None, "second-key"),
    ]


async def test_direct_request_does_not_inject_key_into_input(async_client, server):
    params = {"q": "coffee"}
    await async_client.request("GET", "/search", params)
    assert params == {"q": "coffee"}
    assert server.last_request.url.params["api_key"] == "test-api-key"


async def test_async_results_are_not_sync_paginators(async_client, server):
    server.handler = lambda request: httpx2.Response(200, json={"page": 1})
    result = await async_client.search()
    assert not isinstance(result, serpapi.SerpResults)
    assert await result.next_page() is None
    assert [page.as_dict() async for page in result.yield_pages()] == [{"page": 1}]
    restored = pickle.loads(pickle.dumps(result))
    assert type(restored) is serpapi.AsyncSerpResults
    assert restored.as_dict() == {"page": 1}


@pytest.mark.parametrize(
    ("output", "content_type"), [("html", "text/html"), ("md", "text/markdown")]
)
async def test_search_returns_text_for_html_and_markdown(
    async_client, server, output, content_type
):
    server.handler = lambda request: httpx2.Response(
        200, text="<h1>Coffee</h1>", headers={"Content-Type": content_type}
    )

    assert await async_client.search(q="coffee", output=output) == "<h1>Coffee</h1>"


@pytest.mark.parametrize(
    ("client_timeout", "request_options", "expected"),
    [
        (None, {}, {"connect": None, "read": None, "write": None, "pool": None}),
        (10, {}, {"connect": 10, "read": 10, "write": 10, "pool": None}),
        (10, {"timeout": 5}, {"connect": 5, "read": 5, "write": 5, "pool": None}),
        (10, {"timeout": (3, 7)}, {"connect": 3, "read": 7, "write": 3, "pool": None}),
        (10, {"timeout": None}, {"connect": None, "read": None, "write": None, "pool": None}),
    ],
)
async def test_timeouts_work_like_requests_timeouts(
    server, client_timeout, request_options, expected
):
    async with serpapi.AsyncClient(api_key="test-api-key", timeout=client_timeout) as client:
        await client.search(q="coffee", **request_options)

    assert server.last_request.extensions["timeout"] == expected


async def test_extract_separates_api_and_http_timeouts(async_client, server):
    params = {"url": "https://example.com", "timeout": 5000}

    await async_client.extract(params, timeout=3)

    assert server.last_request.url.params["engine"] == "extract"
    assert server.last_request.url.params["timeout"] == "5000"
    assert server.last_request.extensions["timeout"]["read"] == 3
    assert params == {"url": "https://example.com", "timeout": 5000}


async def test_search_archive(async_client, server):
    with pytest.raises(serpapi.SearchIDNotProvided):
        await async_client.search_archive()

    results = await async_client.search_archive(search_id="abc123")

    assert isinstance(results, serpapi.AsyncSerpResults)
    assert server.last_request.url.path == "/searches/abc123"


async def test_upload_image_sends_multipart_request(async_client, server, tmp_path):
    image_path = tmp_path / "test.png"
    image_path.write_bytes(b"fake-png-data")
    server.handler = lambda request: httpx2.Response(200, json={"image_id": "image-123"})

    result = await async_client.upload_image(image_path, zero_trace=True, timeout=5)

    assert result == {"image_id": "image-123"}
    request = server.last_request
    assert request.method == "POST"
    assert str(request.url) == "https://serpapi.com/image"
    assert request.extensions["timeout"]["read"] == 5
    assert request.headers["Content-Type"].startswith("multipart/form-data; boundary=")
    assert b'name="zero_trace"\r\n\r\nTrue\r\n' in request.content
    assert b'name="api_key"\r\n\r\ntest-api-key\r\n' in request.content
    assert b'name="image"; filename="test.png"\r\n\r\nfake-png-data\r\n' in request.content


async def test_upload_image_rejects_text_mode_file(async_client, server, tmp_path):
    image_path = tmp_path / "test.png"
    image_path.write_text("fake-png-data")

    with image_path.open("r") as image, pytest.raises(TypeError, match="binary mode"):
        await async_client.upload_image(image)

    assert server.requests == []


async def test_upload_reads_files_off_the_event_loop(async_client, server, tmp_path, monkeypatch):
    image_path = tmp_path / "test.png"
    image_path.write_bytes(b"image-data")
    threads = []
    real_open = open

    class Image(io.BytesIO):
        name = "test.png"

        def read(self, *args):
            threads.append(threading.get_ident())
            return super().read(*args)

    def open_image(path, *args, **kwargs):
        if path == image_path:
            threads.append(threading.get_ident())
            return Image(b"image-data")
        return real_open(path, *args, **kwargs)

    monkeypatch.setattr("builtins.open", open_image)
    borrowed = Image(b"image-data")
    for image in (image_path, borrowed):
        await async_client.upload_image(image)
        assert b'filename="test.png"\r\n\r\nimage-data\r\n' in server.last_request.content
    assert len(threads) == 3 and threading.get_ident() not in threads
    assert not borrowed.closed


async def test_cancelled_upload_finishes_read_before_returning_borrowed_file(async_client, server):
    loop = asyncio.get_running_loop()
    started = asyncio.Event()
    release = threading.Event()

    class Image(io.BytesIO):
        def read(self):
            loop.call_soon_threadsafe(started.set)
            assert release.wait(timeout=5)
            return super().read()

    with Image(b"image") as image:
        before = asyncio.all_tasks()
        upload = asyncio.create_task(async_client.upload_image(image))
        try:
            await asyncio.wait_for(started.wait(), timeout=5)
            # Application shutdown may cancel both the upload and its child tasks.
            for task in asyncio.all_tasks() - before:
                task.cancel()
            await asyncio.sleep(0)
            assert not upload.done()
        finally:
            release.set()
            with pytest.raises(asyncio.CancelledError):
                await upload
        assert image.tell() == len(b"image")
    assert not server.requests


async def test_locations_and_account_return_json(async_client, server):
    def handler(request):
        if request.url.path == "/locations.json":
            return httpx2.Response(200, json=[{"name": "Austin"}])
        return httpx2.Response(200, json={"plan_name": "Free"})

    server.handler = handler

    assert await async_client.locations(q="Austin", limit=3) == [{"name": "Austin"}]
    assert server.last_request.url.params["limit"] == "3"
    assert await async_client.account() == {"plan_name": "Free"}
    assert server.last_request.url.path == "/account.json"


async def test_error_status_raises_http_error_without_the_api_key(async_client, server):
    server.handler = lambda request: httpx2.Response(401, json={"error": "Invalid API key."})

    with pytest.raises(serpapi.HTTPError) as exc_info:
        await async_client.search(q="coffee")

    assert exc_info.value.status_code == 401
    assert exc_info.value.error == "Invalid API key."
    assert isinstance(exc_info.value.response, httpx2.Response)
    assert str(exc_info.value) == (
        "401 Client Error: Unauthorized for url: https://serpapi.com/search?q=coffee"
    )

    response = await async_client.request("GET", "/search", {}, assert_200=False)
    assert response.status_code == 401


async def test_error_status_without_json_has_no_error_message(async_client, server):
    server.handler = lambda request: httpx2.Response(503, text="<html>Unavailable</html>")

    with pytest.raises(serpapi.HTTPError) as exc_info:
        await async_client.account()

    assert exc_info.value.status_code == 503
    assert exc_info.value.error is None


async def test_http_logs_redact_api_key_from_search_and_pagination(
    async_client, server, caplog
):
    server.handler = lambda request: httpx2.Response(
        200,
        json={
            "serpapi_pagination": {
                "next": "https://serpapi.com/search?start=10",
            }
        },
    )
    caplog.set_level(logging.INFO, logger="httpx2")

    results = await async_client.search(q="coffee")
    await results.next_page()

    http_logs = [
        record.getMessage()
        for record in caplog.records
        if record.name == "httpx2" and record.getMessage().startswith("HTTP Request:")
    ]
    assert len(http_logs) == 2
    assert all("test-api-key" not in message for message in http_logs)
    assert all("api_key=<redacted>" in message for message in http_logs)
    assert "q=coffee" in http_logs[0]
    assert "start=10" in http_logs[1]


async def test_http_logs_only_redact_sdk_request_urls(async_client, server, caplog):
    async def handler(request):
        if request.url.path == "/search":
            await async_client.session.get("https://example.test/other?api_key=test-api-key")
            return httpx2.Response(302, headers={"Location": "/redirect?api_key=redirect-key"})
        return httpx2.Response(200, json={})

    server.handler = handler
    caplog.set_level(logging.INFO, logger="httpx2")
    await asyncio.gather(
        async_client.search(), async_client.session.get("https://example.test/raw?api_key=raw-key")
    )
    records = [r for r in caplog.records if r.name == "httpx2"]
    assert len(records) == 4 and all(len(r.args) == 5 for r in records)
    for path, key in (("other", "test-api-key"), ("raw", "raw-key")):
        record = next(r for r in records if "/{}?".format(path) in r.getMessage())
        assert isinstance(record.args[1], httpx2.URL) and record.args[1].params["api_key"] == key
    for path in ("search", "redirect"):
        record = next(r for r in records if "/{}?".format(path) in r.getMessage())
        assert "api_key=<redacted>" in record.getMessage()
        assert record.msg.startswith("HTTP Request: %s %s")


async def test_http_logs_protect_keys_when_auth_rebuilds_the_request(async_client, server, caplog):
    class RebuildRequest(httpx2.Auth):
        async def async_auth_flow(self, request):
            response = yield request
            if response.status_code == 401:
                yield httpx2.Request(request.method, request.url.copy_set_param("api_key", "retry-key"))

    server.handler = lambda r: httpx2.Response(200 if r.url.params["api_key"] == "retry-key" else 401)
    caplog.set_level(logging.INFO, logger="httpx2")
    await async_client.request("GET", "/search", {}, auth=RebuildRequest())
    assert [r.url.params["api_key"] for r in server.requests] == ["test-api-key", "retry-key"]
    assert "test-api-key" not in caplog.text and "retry-key" not in caplog.text
    assert caplog.text.count("api_key=<redacted>") == 2


@pytest.mark.parametrize("source", ["session", "request_hook", "auth"])
async def test_http_logs_redact_the_key_on_the_final_request(server, caplog, source):
    key = "late-fixture-key"

    async def add_key(request):
        request.url = request.url.copy_set_param("api_key", key)

    class ReplaceRequest(httpx2.Auth):
        def auth_flow(self, request):
            yield httpx2.Request(request.method, request.url.copy_set_param("api_key", key))

    caplog.set_level(logging.INFO, logger="httpx2")
    async with serpapi.AsyncClient() as client:
        if source == "session":
            client.session.params = {"api_key": key}
        elif source == "request_hook":
            client.session.event_hooks = {"request": [add_key]}
        else:
            client.session.auth = ReplaceRequest()
        await client.search(q="coffee")

    assert server.last_request.url.params["api_key"] == key
    assert server.last_request.url.params["q"] == "coffee"
    record, = [r for r in caplog.records if r.name == "httpx2"]
    assert key not in record.getMessage() and key not in str(record.args[1])
    assert "api_key=<redacted>" in record.getMessage()
    assert record.msg.startswith("HTTP Request: %s %s")


async def test_corrupt_content_is_a_requests_decoding_error(async_client, server):
    server.handler = lambda r: httpx2.Response(
        200, headers={"Content-Encoding": "gzip"}, stream=httpx2.ByteStream(b"invalid gzip")
    )
    with pytest.raises(requests.exceptions.ContentDecodingError) as exc:
        await async_client.account()
    assert isinstance(exc.value.__cause__, httpx2.DecodingError)


@pytest.mark.parametrize(("native", "mapped"), [
    (httpx2.TooManyRedirects, requests.exceptions.TooManyRedirects),
    (httpx2.UnsupportedProtocol, requests.exceptions.InvalidSchema),
    (httpx2.RequestError, requests.exceptions.RequestException),
])
async def test_other_transport_errors_reach_requests_handlers(async_client, server, native, mapped):
    def handler(request):
        raise native("test transport failure", request=request)

    server.handler = handler
    with pytest.raises(mapped) as exc:
        await async_client.search()
    assert isinstance(exc.value.__cause__, native)
    assert exc.value.request is server.last_request


@pytest.mark.parametrize(
    ("exception", "expected", "message", "expected_message"),
    [
        (httpx2.ConnectTimeout, serpapi.HTTPConnectionError, "failed", "failed"),
        (httpx2.ConnectError, serpapi.HTTPConnectionError, "failed", "failed"),
        (httpx2.RemoteProtocolError, serpapi.HTTPConnectionError, "failed", "failed"),
        (httpx2.ReadTimeout, serpapi.TimeoutError, "failed", "failed"),
        (httpx2.ReadTimeout, serpapi.TimeoutError, "", "The request timed out."),
    ],
)
async def test_transport_errors_raise_serpapi_errors(
    async_client, server, exception, expected, message, expected_message
):
    def handler(request):
        raise exception(message, request=request)

    server.handler = handler

    with pytest.raises(expected) as exc_info:
        await async_client.search(q="coffee")

    assert isinstance(exc_info.value.__cause__, exception)
    if expected is serpapi.TimeoutError:
        assert str(exc_info.value) == expected_message


@pytest.mark.parametrize("method", ["account", "locations", "upload_image"])
@pytest.mark.parametrize(
    "body",
    [b"<html>Proxy sign-in required</html>", b"<html>Acc\xe8s refus\xe9</html>"],
    ids=["utf-8", "latin-1"],
)
async def test_dictionary_methods_wrap_json_decode_errors(
    async_client, server, method, body, tmp_path
):
    server.handler = lambda request: httpx2.Response(
        200, content=body, headers={"Content-Type": "text/html"}
    )
    arguments = ()
    if method == "upload_image":
        image = tmp_path / "image.png"
        image.write_bytes(b"image-bytes")
        arguments = (image,)

    with pytest.raises(requests.exceptions.JSONDecodeError) as exc_info:
        await getattr(async_client, method)(*arguments)

    assert isinstance(exc_info.value, requests.exceptions.RequestException)
    assert isinstance(exc_info.value.__cause__, json.JSONDecodeError)


async def test_dictionary_methods_decode_json_with_the_response_charset(async_client, server):
    server.handler = lambda request: httpx2.Response(
        200,
        content=b'{"plan_name": "Caf\xe9"}',
        headers={"Content-Type": "application/json; charset=iso-8859-1"},
    )

    assert await async_client.account() == {"plan_name": "Caf\u00e9"}


@pytest.mark.parametrize(
    "charset,expected", [("gb18030", "\u6bdb"), ("latin1", "\u00c3\u00ab")]
)
async def test_declared_charset_takes_precedence_over_valid_utf8(async_client, server, charset, expected):
    def respond(request, status=200):
        return httpx2.Response(
            status, content=b'{"error":"\xc3\xab"}',
            headers={"Content-Type": f"application/json; charset={charset}"},
        )

    server.handler = respond
    assert (await async_client.search(q="coffee"))["error"] == expected
    assert (await async_client.account())["error"] == expected

    server.handler = lambda request: respond(request, 401)
    with pytest.raises(serpapi.HTTPError) as exc_info:
        await async_client.account()
    assert exc_info.value.error == expected


@pytest.mark.parametrize("charset", ["utf8", "base64", "unknown-charset"])
async def test_json_byte_decoder_preserves_utf8_bom(async_client, server, charset):
    server.handler = lambda request: httpx2.Response(
        200, content=b'\xef\xbb\xbf{"value":1}',
        headers={"Content-Type": f"application/json; charset={charset}"},
    )
    assert await async_client.account() == {"value": 1}


async def test_results_decode_json_with_the_response_charset(async_client, server):
    server.handler = lambda request: httpx2.Response(
        200,
        content=(
            b'{"title": "Caf\xe9", '
            b'"serpapi_pagination": {"next": "https://serpapi.com/search?start=10"}}'
        ),
        headers={"Content-Type": "application/json; charset=iso-8859-1"},
    )

    results = await async_client.search(q="coffee")
    next_results = await results.next_page()

    assert isinstance(results, serpapi.AsyncSerpResults)
    assert isinstance(next_results, serpapi.AsyncSerpResults)
    assert next_results["title"] == "Caf\u00e9"


async def test_error_status_decodes_json_with_the_response_charset(async_client, server):
    server.handler = lambda request: httpx2.Response(
        401,
        content=b'{"error": "Cl\xe9 API invalide"}',
        headers={"Content-Type": "application/json; charset=iso-8859-1"},
    )

    with pytest.raises(serpapi.HTTPError) as exc_info:
        await async_client.search(q="coffee")

    assert exc_info.value.error == "Cl\u00e9 API invalide"


async def test_tls_alerts_raise_connection_errors(async_client, server):
    def handler(request):
        raise ssl.SSLError("TLS peer requires a client certificate")

    server.handler = handler
    with pytest.raises(serpapi.HTTPConnectionError) as exc_info:
        await async_client.search(q="coffee")
    assert isinstance(exc_info.value.__cause__, ssl.SSLError)


@pytest.mark.parametrize("timeout", [0, -1, True, (1, 2, 3), (1, -1)])
async def test_invalid_timeouts_are_rejected_like_requests(async_client, server, timeout):
    with pytest.raises(ValueError):
        await async_client.search(q="coffee", timeout=timeout)
    assert not server.requests


@pytest.mark.parametrize(
    ("max_pages", "available_pages", "expected_pages"),
    [(1, 3, 1), (2, 3, 2), (3, 3, 3), (5, 3, 3), (5, 1, 1), (0, 3, 0)],
)
async def test_yield_pages_does_not_request_unused_pages(
    async_client, server, max_pages, available_pages, expected_pages
):
    def handler(request):
        page_number = int(request.url.params.get("start", 0)) // 10 + 1
        data = {"search_information": {"page_number": page_number}}
        if page_number < available_pages:
            data["serpapi_pagination"] = {
                "next": f"https://serpapi.com/search?engine=google&q=Coffee&start={page_number * 10}"
            }
        return httpx2.Response(200, json=data)

    server.handler = handler
    results = await async_client.search(engine="google", q="Coffee")

    pages = [page async for page in results.yield_pages(max_pages=max_pages)]

    assert [page["search_information"]["page_number"] for page in pages] == list(
        range(1, expected_pages + 1)
    )
    assert len(server.requests) == max(1, expected_pages)
    assert all(request.url.params["api_key"] == "test-api-key" for request in server.requests)


async def test_requests_run_concurrently(async_client, server):
    arrived = []
    all_arrived = asyncio.Event()

    async def handler(request):
        arrived.append(request)
        if len(arrived) == 3:
            all_arrived.set()
        # Each response waits for all three requests, so they must be sent at the same time.
        await all_arrived.wait()
        return httpx2.Response(200, json={"q": request.url.params["q"]})

    server.handler = handler

    results = await asyncio.wait_for(
        asyncio.gather(*(async_client.search(q=q) for q in ["a", "b", "c"])), timeout=5
    )

    assert [result["q"] for result in results] == ["a", "b", "c"]


async def test_request_options_use_cached_sessions(async_client, server):
    proxies = {"https": "http://proxy.example:8080"}

    await async_client.search(q="coffee", proxies=proxies)
    await async_client.search(q="tea", proxies=dict(proxies))
    await async_client.search(q="coffee", verify=False)
    await async_client.search(q="coffee")

    assert len(server.pools) == 3
    (default, _), (proxy, _), (no_verify, _) = server.pools
    assert default["proxy"] is None
    assert default["trust_env"] is False
    assert proxy["proxy"] == "http://proxy.example:8080"
    assert proxy["trust_env"] is False
    assert no_verify["verify"].verify_mode == ssl.CERT_NONE
    assert async_client.session.follow_redirects is True
    assert async_client.session.timeout == httpx2.Timeout(None)


async def test_cached_session_uses_current_request_and_response_hooks(async_client, server):
    events = []

    async def old(request):
        events.append("old")
        async_client.session.event_hooks["response"].append(after)

    async def before(request):
        events.append("request")

    async def after(response):
        events.append("response")

    async_client.session.event_hooks = {"request": [old]}
    await async_client.search(verify=False)
    async_client.session.event_hooks = {"request": [before]}
    async_client.session.event_hooks["response"].append(after)
    await async_client.search(verify=False)
    assert events == ["old", "response", "request", "response"]


async def test_redirect_runs_current_hooks_once_per_hop(async_client, server, monkeypatch):
    monkeypatch.setattr(async_client, "_MAX_OPTION_POOLS", 0)
    events = []

    async def before(request):
        events.append(("request", request.url.path))

    async def after(response):
        events.append(("response", response.request.url.path))

    def handle(request):
        if request.url.path == "/start":
            return httpx2.Response(302, headers={"Location": "https://other.test/end"})
        return httpx2.Response(200)

    server.handler = handle
    async_client.session.event_hooks = {"request": [before], "response": [after]}
    await async_client.request("GET", "/start", {}, proxies={"https://serpapi.com": "http://proxy.test"})
    assert events == [
        ("request", "/start"), ("response", "/start"), ("request", "/end"), ("response", "/end"),
    ]
    assert len(server.pools) == 2 and server.pools[-1][1].is_closed


@pytest.mark.parametrize("proxied_host", ["serpapi.com", "mirror.test"])
async def test_request_hook_selects_proxy_for_final_host(async_client, server, proxied_host):
    async def rewrite(request):
        request.url = request.url.copy_with(host="mirror.test")

    async_client.session.event_hooks["request"].append(rewrite)
    proxy = "http://proxy.test"
    await async_client.search(proxies={"https://" + proxied_host: proxy})
    assert server.last_request.url.host == "mirror.test"
    assert server.sent_via == [proxy if proxied_host == "mirror.test" else None]


async def test_sessions_beyond_the_cache_limit_close_after_the_request(
    async_client, server, monkeypatch
):
    monkeypatch.setattr(async_client, "_MAX_OPTION_POOLS", 1)

    await async_client.search(q="coffee", verify=False)
    await async_client.search(q="coffee", proxies={"https": "http://proxy.example:8080"})

    (_, default), (_, cached), (_, temporary) = server.pools
    assert not cached.is_closed
    assert temporary.is_closed


async def test_proxy_sessions_reuse_only_the_clients_default_trust(async_client, server, monkeypatch):
    monkeypatch.setattr(async_client, "_MAX_OPTION_POOLS", 0)
    default_context = server.pools[0][0]["verify"]
    await async_client.search(proxies={"https": "http://first.test:8080"})
    await async_client.search(proxies={"https": "http://second.test:8080"})
    assert all(options["verify"] is default_context for options, _ in server.pools)
    async with serpapi.AsyncClient():
        assert server.pools[-1][0]["verify"] is not default_context


@pytest.mark.parametrize("tls", [{"verify": certifi.where()}, {"cert": "client.pem"}])
async def test_custom_tls_files_load_once_across_proxies(async_client, server, monkeypatch, tls):
    monkeypatch.setattr(async_client, "_MAX_OPTION_POOLS", 1)
    monkeypatch.setattr(ssl.SSLContext, "load_cert_chain", lambda ctx, *args: None)
    loaded = []
    load = ssl.SSLContext.load_verify_locations
    monkeypatch.setattr(
        ssl.SSLContext, "load_verify_locations",
        lambda ctx, *args, **kwargs: loaded.append(ctx) or load(ctx, *args, **kwargs),
    )
    # One cached pool, then temporary pools beyond the cache limit.
    for host in ("first", "second", "third"):
        await async_client.search(proxies={"https": f"http://{host}.test:8080"}, **tls)
    assert len(loaded) == 1
    assert all(options["verify"] is loaded[0] for options, _ in server.pools[1:])


async def test_default_trust_never_inherits_a_client_certificate(async_client, server, monkeypatch):
    loaded = []
    monkeypatch.setattr(ssl.SSLContext, "load_cert_chain", lambda ctx, *args: loaded.append(ctx))
    default = server.pools[0][0]["verify"]
    await async_client.search(cert="client.pem", proxies={"https": "https://proxy.test"})
    options = server.pools[-1][0]
    assert loaded == [options["verify"]] and options["verify"] is not default
    assert options["proxy"].ssl_context is default


@pytest.mark.parametrize("method", ["__aenter__", "search", "aclose"])
def test_rejects_use_without_an_asyncio_loop_before_doing_work(server, method):
    client = serpapi.AsyncClient()
    action = getattr(client, method)()
    try:
        with pytest.raises(RuntimeError, match="requires asyncio"):
            action.send(None)
        assert not server.requests and not client._closed
    finally:
        action.close()
        asyncio.run(client.aclose())


async def test_closed_client_cannot_send_requests_or_reopen(server):
    client = serpapi.AsyncClient(api_key="test-api-key")
    await client.search(q="coffee", verify=False)

    await client.aclose()
    await client.aclose()

    assert all(session.is_closed for _, session in server.pools)
    with pytest.raises(RuntimeError, match="closed"):
        await client.search(q="coffee")
    with pytest.raises(RuntimeError, match="reopen"):
        async with client:
            pass


async def test_aclose_finishes_closing_sessions_when_caller_is_cancelled(
    server, monkeypatch
):
    client = serpapi.AsyncClient(api_key="test-api-key")
    await client.search(q="coffee", verify=False)
    sessions = [client.session, *client._option_pools.values()]

    close_started = asyncio.Event()
    allow_close = asyncio.Event()
    original_aclose = client.session.aclose

    async def delayed_close():
        close_started.set()
        await allow_close.wait()
        await original_aclose()

    monkeypatch.setattr(client.session, "aclose", delayed_close)
    close_caller = asyncio.create_task(client.aclose())
    try:
        await close_started.wait()
        close_caller.cancel()
        with pytest.raises(asyncio.CancelledError):
            await close_caller

        # The close carries on in the background, without another aclose() call.
        background_close = client._close_task
        allow_close.set()
        await background_close

        assert all(session.is_closed for session in sessions)
        assert client._close_task is None
        assert not client._option_pools
    finally:
        allow_close.set()
        await client.aclose()


async def test_aclose_can_be_retried_after_the_background_close_fails(server, monkeypatch):
    client = serpapi.AsyncClient(api_key="test-api-key")
    close_started = asyncio.Event()
    allow_close = asyncio.Event()
    original_aclose = client.session.aclose
    close_error = OSError("close failed")

    async def failing_close():
        close_started.set()
        await allow_close.wait()
        raise close_error

    monkeypatch.setattr(client.session, "aclose", failing_close)
    close_caller = asyncio.create_task(client.aclose())
    await close_started.wait()
    close_caller.cancel()
    with pytest.raises(asyncio.CancelledError):
        await close_caller

    background_close = client._close_task
    loop = asyncio.get_running_loop()
    original_exception_handler = loop.call_exception_handler

    def handle_expected_close_error(context):
        if context.get("future") is background_close and context.get("exception") is close_error:
            return
        original_exception_handler(context)

    # Python 3.14 also reports the expected failure through the cancelled shield.
    with monkeypatch.context() as patch:
        patch.setattr(loop, "call_exception_handler", handle_expected_close_error)
        allow_close.set()
        with pytest.raises(OSError, match="close failed"):
            await background_close

    monkeypatch.setattr(client.session, "aclose", original_aclose)
    await client.aclose()

    assert client.session.is_closed


async def test_closed_client_does_not_create_new_sessions(async_client):
    await async_client.aclose()

    with pytest.raises(RuntimeError, match="closed"):
        async_client._pool_for(
            "https://serpapi.com/search",
            {"https": "http://proxy.example:8080"},
            None,
            None,
        )


def test_select_proxy_merges_environment_proxies_like_requests(monkeypatch):
    for name in ["http_proxy", "https_proxy", "all_proxy", "no_proxy"]:
        monkeypatch.delenv(name, raising=False)
        monkeypatch.delenv(name.upper(), raising=False)
    monkeypatch.setenv("HTTPS_PROXY", "env-proxy.example:3128")
    url = "https://serpapi.com/search"

    assert _select_proxy(url, {"http": "http://other.example:8080"}) == (
        "http://env-proxy.example:3128"
    )
    assert _select_proxy(url, {"https": "http://proxy.example:8080"}) == (
        "http://proxy.example:8080"
    )
    assert _select_proxy(url, {"https": None}) is None
    assert _select_proxy(url, {"http": "http://other.example:8080", "no_proxy": "serpapi.com"}) is None


def test_ssl_context_supports_requests_verify_options(monkeypatch):
    assert _ssl_context(httpx2, False, None).verify_mode == ssl.CERT_NONE
    assert _ssl_context(httpx2, certifi.where(), None).get_ca_certs()

    monkeypatch.setenv("REQUESTS_CA_BUNDLE", certifi.where())
    assert _ssl_context(httpx2, None, None).get_ca_certs()

    with pytest.raises(TypeError, match="load_cert_chain"):
        _ssl_context(httpx2, ssl.create_default_context(), "client.pem")


def test_default_tls_uses_certifi_not_ssl_environment(monkeypatch, tmp_path):
    monkeypatch.setenv("SSL_CERT_FILE", str(tmp_path / "missing.pem"))
    monkeypatch.setenv("SSL_CERT_DIR", str(tmp_path / "missing-directory"))

    context = _ssl_context(httpx2, True, None)
    expected = ssl.create_default_context(cafile=requests.certs.where())

    assert context.verify_mode == ssl.CERT_REQUIRED
    assert context.check_hostname
    assert context.get_ca_certs(binary_form=True) == expected.get_ca_certs(binary_form=True)


async def test_proxy_environment_is_resolved_for_each_request(async_client, server, monkeypatch):
    monkeypatch.setenv("HTTPS_PROXY", "http://first.example:8080")
    await async_client.search(q="coffee")
    assert server.pools[-1][0]["proxy"] == "http://first.example:8080"

    monkeypatch.setenv("HTTPS_PROXY", "http://second.example:8080")
    await async_client.search(q="tea")
    assert server.pools[-1][0]["proxy"] == "http://second.example:8080"

    monkeypatch.setenv("NO_PROXY", "serpapi.com")
    await async_client.search(q="water")
    assert len(server.pools) == 3
    assert server.pools[0][0]["trust_env"] is False


@pytest.mark.parametrize("variable", ["REQUESTS_CA_BUNDLE", "CURL_CA_BUNDLE"])
async def test_ca_environment_is_resolved_for_each_request(
    async_client, server, monkeypatch, tmp_path, variable
):
    bundle = tmp_path / "ca.pem"
    bundle.write_bytes(Path(certifi.where()).read_bytes())
    monkeypatch.setenv(variable, str(bundle))

    await async_client.search(q="coffee", verify=True)

    assert len(server.pools) == 2
    assert server.pools[-1][0]["verify"].get_ca_certs()

    monkeypatch.setenv(variable, str(tmp_path / "missing.pem"))
    with pytest.raises(OSError):
        await async_client.search(q="tea")


async def test_https_proxy_uses_the_request_tls_context(async_client, server):
    await async_client.search(proxies={"https": "https://proxy.example:8443"}, verify=False)

    options, _ = server.pools[-1]
    assert isinstance(options["proxy"], httpx2.Proxy)
    assert options["proxy"].ssl_context is options["verify"]
    assert options["proxy"].ssl_context.verify_mode == ssl.CERT_NONE


async def test_https_proxy_is_not_offered_the_client_certificate(
    async_client, server, monkeypatch
):
    with_client_certificate = []
    monkeypatch.setattr(
        ssl.SSLContext,
        "load_cert_chain",
        lambda context, *args, **kwargs: with_client_certificate.append(context),
    )

    await async_client.search(
        proxies={"https": "https://proxy.example:8443"}, verify=False, cert="client.pem"
    )

    options, _ = server.pools[-1]
    assert with_client_certificate == [options["verify"]]
    assert options["proxy"].ssl_context is not options["verify"]
    assert options["proxy"].ssl_context.verify_mode == ssl.CERT_NONE


async def test_redirects_reselect_the_proxy_for_the_destination(async_client, server):
    def handler(request):
        if request.url.scheme == "http":
            return httpx2.Response(302, headers={"Location": "https://serpapi.com/search"})
        return httpx2.Response(200, json={})

    server.handler = handler
    await async_client.request("GET", "http://serpapi.com/search", {}, proxies={
        "http": "http://first.example:8080", "https": "http://second.example:8080",
    })
    assert [options["proxy"] for options, _ in server.pools] == [
        None, "http://first.example:8080", "http://second.example:8080",
    ]


@pytest.mark.parametrize("target,disable_auth,expected", [
    ("/done", True, [False, False]),
    ("https://other.test/done", False, [True, False]),
])
async def test_redirect_does_not_restart_session_auth(async_client, server, target, disable_auth, expected):
    async_client.session.auth = ("fixture", "fixture")
    server.handler = lambda r: (
        httpx2.Response(302, headers={"Location": target}) if r.url.path == "/start"
        else httpx2.Response(200)
    )
    options = {"auth": None} if disable_auth else {}
    await async_client.request("GET", "/start", {}, **options)
    assert ["Authorization" in r.headers for r in server.requests] == expected


def _header_auth(request):
    request.headers["X-Test-Auth"] = "callable"
    return request


# Client sends the same headers through requests for each of these auth forms.
@pytest.mark.parametrize("path,options,header,value", [
    ("/search", {"auth": ("user", "pass")}, "Authorization", "Basic dXNlcjpwYXNz"),
    ("https://user:pass@serpapi.com/search", {}, "Authorization", "Basic dXNlcjpwYXNz"),
    ("/search", {"auth": _header_auth}, "X-Test-Auth", "callable"),
])
async def test_request_auth_forms_match_client(async_client, server, path, options, header, value):
    await async_client.request("GET", path, {}, **options)
    assert server.last_request.headers.get(header) == value


async def test_invalid_auth_raises_type_error_before_sending(async_client, server):
    with pytest.raises(TypeError, match='Invalid "auth" argument'):
        await async_client.request("GET", "/search", {}, auth=123)
    assert server.requests == []


async def test_auth_receives_redirect_destination_before_retry(async_client, server):
    statuses = []

    class Challenge(httpx2.Auth):
        async def async_auth_flow(self, request):
            response = yield request
            statuses.append(response.status_code)
            if response.status_code == 401:
                retry = httpx2.Request("GET", response.url)
                retry.headers["X-Test-Retry"] = "1"
                response = yield retry
                statuses.append(response.status_code)

    def handler(request):
        if request.url.path == "/start":
            return httpx2.Response(302, headers={"Location": "/challenge"})
        return httpx2.Response(200 if "X-Test-Retry" in request.headers else 401)

    server.handler = handler
    response = await async_client.request("GET", "/start", {}, auth=Challenge(), assert_200=False)
    assert statuses == [401, 200]
    assert response.status_code == 200


async def test_auth_can_reject_headers_before_reading_the_body(async_client, server, monkeypatch):
    events = []

    class SlowBody(httpx2.AsyncByteStream):
        async def __aiter__(self):
            events.append("read")
            yield b"partial"
            raise httpx2.ReadTimeout("body timeout")

        async def aclose(self):
            events.append("closed")

    class Reject(httpx2.Auth):
        async def async_auth_flow(self, request):
            response = yield request
            assert response.status_code == 403
            assert not server.pools[-1][1].is_closed
            raise ValueError("auth rejected response")

    monkeypatch.setattr(async_client, "_MAX_OPTION_POOLS", 0)
    server.handler = lambda request: httpx2.Response(403, stream=SlowBody())
    with pytest.raises(ValueError, match="auth rejected response"):
        await async_client.request("GET", "/search", {}, auth=Reject(), verify=False)
    assert events == ["closed"]
    assert server.pools[-1][1].is_closed


@pytest.mark.parametrize("redirects", [25, 31])
async def test_redirect_limit_matches_requests(async_client, server, redirects):
    def handler(request):
        remaining = int(request.url.params["redirects"])
        if remaining:
            return httpx2.Response(
                302, headers={"Location": "/search?redirects={}".format(remaining - 1)},
                stream=httpx2.ByteStream(b"redirect"),
            )
        return httpx2.Response(200, json={"done": True})

    server.handler = handler
    if redirects > 30:
        with pytest.raises(requests.exceptions.TooManyRedirects) as exc:
            await async_client.search(redirects=redirects)
        assert exc.value.response.status_code == 302
        assert exc.value.response.content == b"redirect"
        assert exc.value.request is exc.value.response.request
    else:
        result = await async_client.search(redirects=redirects)
        assert result["done"]


def redirect_to(location):
    return lambda request: (
        httpx2.Response(302, headers={"Location": location}, json={"redirect": True})
        if request.url.path == "/search" else httpx2.Response(200, json={"followed": True})
    )


@pytest.mark.parametrize("location,expected", [
    ("http://127.0.0.1:bad/", requests.exceptions.InvalidURL),
    ("http://[::1/done", requests.exceptions.InvalidURL),
    ("http://127.0.0.1:99999/done", requests.exceptions.InvalidURL),
    ("mailto:user@example.com", requests.exceptions.InvalidSchema),
])
async def test_invalid_redirect_targets_raise_requests_errors(async_client, server, location, expected):
    server.handler = redirect_to(location)
    with pytest.raises(expected) as exc:
        await async_client.search()
    assert type(exc.value) is expected
    assert exc.value.response.status_code == 302
    assert exc.value.response.json() == {"redirect": True}
    assert [r.url.path for r in server.requests] == ["/search"]


async def test_unfollowed_invalid_redirect_is_returned(async_client, server):
    server.handler = redirect_to("http://127.0.0.1:bad/")
    response = await async_client.request("GET", "/search", {}, allow_redirects=False)
    assert response.status_code == 302 and response.next_request is None


async def test_empty_redirect_location_returns_the_response_like_client(async_client, server):
    server.handler = redirect_to("")
    assert await async_client.search() == {"redirect": True}
    assert len(server.requests) == 1


async def test_only_unfollowed_redirects_keep_next_request(async_client, server):
    server.handler = redirect_to("/done")
    followed = await async_client.request("GET", "/search", {})
    unfollowed = await async_client.request("GET", "/search", {}, allow_redirects=False)
    assert [r.next_request for r in followed.history] == [None]
    assert unfollowed.next_request.url.path == "/done"


async def test_cookies_survive_request_option_changes(async_client, server):
    server.handler = lambda request: httpx2.Response(
        200, json={}, headers={"Set-Cookie": "session=local-value; Path=/"}
    )
    await async_client.search(q="coffee")
    await async_client.search(q="tea", verify=False)
    assert server.last_request.headers["Cookie"] == "session=local-value"
