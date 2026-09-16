from unittest.mock import Mock

import httpx

import serpapi


def json_response(url="https://serpapi.com/search"):
    request = httpx.Request("GET", url)
    return httpx.Response(200, json={"ok": True}, request=request)


def test_sync_client_context_manager_closes_session():
    with serpapi.Client(api_key="test-key") as client:
        session = client.session
        assert not session.is_closed
    assert session.is_closed


def test_client_default_preserves_no_timeout_and_redirect_behavior():
    client = serpapi.Client(api_key="test-key")
    try:
        assert client.session.timeout.connect is None
        assert client.session.timeout.read is None
        assert client.session.follow_redirects is True
    finally:
        client.close()


def test_pagination_url_keeps_repeated_query_parameters():
    captured = []

    def handler(request):
        captured.append(request)
        return httpx.Response(200, json={"ok": True})

    client = serpapi.Client(api_key="test-key")
    client.session.close()
    client.session = httpx.Client(transport=httpx.MockTransport(handler))
    try:
        client.request(
            "GET",
            "https://serpapi.com/search?filter=a&filter=b&page=2",
            params={},
        )
    finally:
        client.close()

    assert captured[0].url.params.multi_items() == [
        ("filter", "a"),
        ("filter", "b"),
        ("page", "2"),
        ("api_key", "test-key"),
    ]


def test_requests_style_per_call_options_use_scoped_httpx_client(monkeypatch):
    created = []

    class ScopedClient:
        def __init__(self, **options):
            self.options = options
            created.append(self)

        def __enter__(self):
            return self

        def __exit__(self, exc_type, exc_value, traceback):
            for transport in self.options.get("mounts", {}).values():
                if transport is not None:
                    transport.close()

        def request(self, **kwargs):
            self.request_kwargs = kwargs
            return json_response(kwargs["url"])

    client = serpapi.Client(api_key="test-key")
    client.session.request = Mock(side_effect=AssertionError("pooled client used"))
    monkeypatch.setattr(httpx, "Client", ScopedClient)
    try:
        result = client.search(
            q="coffee",
            proxies={"https": "http://proxy.example.com:8080"},
            verify=False,
            stream=True,
        )
    finally:
        client.close()

    assert result == {"ok": True}
    assert len(created) == 1
    assert created[0].options["verify"] is False
    assert "https://" in created[0].options["mounts"]
    assert "stream" not in created[0].request_kwargs


def test_sync_client_translates_connection_and_timeout_errors():
    request = httpx.Request("GET", "https://serpapi.com/search")
    client = serpapi.Client(api_key="test-key")
    try:
        client.session.request = Mock(
            side_effect=httpx.ConnectError("failed", request=request)
        )
        try:
            client.search(q="coffee")
        except serpapi.HTTPConnectionError as error:
            assert isinstance(error.__cause__, httpx.ConnectError)
        else:
            raise AssertionError("Expected HTTPConnectionError")

        client.session.request = Mock(
            side_effect=httpx.ReadTimeout("slow", request=request)
        )
        try:
            client.search(q="coffee")
        except serpapi.TimeoutError as error:
            assert isinstance(error.__cause__, httpx.ReadTimeout)
        else:
            raise AssertionError("Expected TimeoutError")
    finally:
        client.close()
