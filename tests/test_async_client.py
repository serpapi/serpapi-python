import asyncio
import json
import logging
import ssl
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
    """Answers and records the requests of every session an AsyncClient creates."""

    def __init__(self):
        self.handler = lambda request: httpx2.Response(200, json={})
        self.requests = []
        # The keyword arguments and httpx2.AsyncClient of each session.
        self.sessions = []

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
    real_async_client = httpx2.AsyncClient

    def async_client(**kwargs):
        # Leave out the proxy and TLS options, so that requests go to the server instead of the network.
        session = real_async_client(
            transport=httpx2.MockTransport(server.handle),
            follow_redirects=kwargs["follow_redirects"],
            timeout=kwargs["timeout"],
            cookies=kwargs.get("cookies"),
        )
        server.sessions.append((kwargs, session))
        return session

    monkeypatch.setattr(httpx2, "AsyncClient", async_client)
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

    assert len(server.sessions) == 3
    (default, _), (proxy, _), (no_verify, _) = server.sessions
    assert default["proxy"] is None
    assert default["trust_env"] is False
    assert proxy["proxy"] == "http://proxy.example:8080"
    assert proxy["trust_env"] is False
    assert no_verify["verify"].verify_mode == ssl.CERT_NONE
    for options, _ in server.sessions:
        assert options["follow_redirects"] is True
        assert options["timeout"] is None


async def test_sessions_beyond_the_cache_limit_close_after_the_request(
    async_client, server, monkeypatch
):
    monkeypatch.setattr(async_client, "_MAX_OPTION_SESSIONS", 1)

    await async_client.search(q="coffee", verify=False)
    await async_client.search(q="coffee", proxies={"https": "http://proxy.example:8080"})

    (_, default), (_, cached), (_, temporary) = server.sessions
    assert not cached.is_closed
    assert temporary.is_closed


async def test_closed_client_cannot_send_requests_or_reopen(server):
    client = serpapi.AsyncClient(api_key="test-api-key")
    await client.search(q="coffee", verify=False)

    await client.aclose()
    await client.aclose()

    assert all(session.is_closed for _, session in server.sessions)
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
    sessions = [client.session, *client._option_sessions.values()]

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
        assert not client._option_sessions
    finally:
        allow_close.set()
        await client.aclose()


async def test_aclose_can_be_retried_after_the_background_close_fails(server, monkeypatch):
    client = serpapi.AsyncClient(api_key="test-api-key")
    close_started = asyncio.Event()
    allow_close = asyncio.Event()
    original_aclose = client.session.aclose

    async def failing_close():
        close_started.set()
        await allow_close.wait()
        raise OSError("close failed")

    monkeypatch.setattr(client.session, "aclose", failing_close)
    close_caller = asyncio.create_task(client.aclose())
    await close_started.wait()
    close_caller.cancel()
    with pytest.raises(asyncio.CancelledError):
        await close_caller

    background_close = client._close_task
    allow_close.set()
    await asyncio.wait({background_close})

    monkeypatch.setattr(client.session, "aclose", original_aclose)
    await client.aclose()

    assert client.session.is_closed


async def test_closed_client_does_not_create_new_sessions(async_client):
    await async_client.aclose()

    with pytest.raises(RuntimeError, match="closed"):
        async_client._session_for(
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
    assert server.sessions[-1][0]["proxy"] == "http://first.example:8080"

    monkeypatch.setenv("HTTPS_PROXY", "http://second.example:8080")
    await async_client.search(q="tea")
    assert server.sessions[-1][0]["proxy"] == "http://second.example:8080"

    monkeypatch.setenv("NO_PROXY", "serpapi.com")
    await async_client.search(q="water")
    assert len(server.sessions) == 3
    assert server.sessions[0][0]["trust_env"] is False


@pytest.mark.parametrize("variable", ["REQUESTS_CA_BUNDLE", "CURL_CA_BUNDLE"])
async def test_ca_environment_is_resolved_for_each_request(
    async_client, server, monkeypatch, tmp_path, variable
):
    bundle = tmp_path / "ca.pem"
    bundle.write_bytes(Path(certifi.where()).read_bytes())
    monkeypatch.setenv(variable, str(bundle))

    await async_client.search(q="coffee", verify=True)

    assert len(server.sessions) == 2
    assert server.sessions[-1][0]["verify"].get_ca_certs()

    monkeypatch.setenv(variable, str(tmp_path / "missing.pem"))
    with pytest.raises(OSError):
        await async_client.search(q="tea")


async def test_https_proxy_uses_the_request_tls_context(async_client, server):
    await async_client.search(proxies={"https": "https://proxy.example:8443"}, verify=False)

    options, _ = server.sessions[-1]
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

    options, _ = server.sessions[-1]
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
    assert [options["proxy"] for options, _ in server.sessions] == [
        None, "http://first.example:8080", "http://second.example:8080",
    ]


@pytest.mark.parametrize("redirects", [25, 31])
async def test_redirect_limit_matches_requests(async_client, server, redirects):
    def handler(request):
        remaining = int(request.url.params["redirects"])
        if remaining:
            return httpx2.Response(302, headers={"Location": "/search?redirects={}".format(remaining - 1)})
        return httpx2.Response(200, json={"done": True})

    server.handler = handler
    if redirects > 30:
        with pytest.raises(httpx2.TooManyRedirects):
            await async_client.search(redirects=redirects)
    else:
        result = await async_client.search(redirects=redirects)
        assert result["done"]


async def test_cookies_survive_request_option_changes(async_client, server):
    server.handler = lambda request: httpx2.Response(
        200, json={}, headers={"Set-Cookie": "session=local-value; Path=/"}
    )
    await async_client.search(q="coffee")
    await async_client.search(q="tea", verify=False)
    assert server.last_request.headers["Cookie"] == "session=local-value"
