import copy
from collections import UserDict
from io import BytesIO
from types import SimpleNamespace
from unittest.mock import patch
from urllib.parse import parse_qs, urlsplit

import pytest
import requests

from serpapi import Client


PARAMS = {
    "search": {"q": "coffee"},
    "search_archive": {"search_id": "example-search"},
    "locations": {"q": "Austin"},
    "account": {},
}


def capture_requests(monkeypatch, client):
    sent = []

    def send(request, **kwargs):
        sent.append(request)
        response = requests.Response()
        response.status_code = 200
        response.headers["Content-Type"] = "application/json"
        response._content = b'{}'
        response.request = request
        return response

    monkeypatch.setattr(client.session, "send", send)
    return sent


@pytest.mark.parametrize("method", list(PARAMS))
@pytest.mark.parametrize("explicit_key", [False, True])
def test_reused_params_keep_each_clients_key(monkeypatch, method, explicit_key):
    first = Client(api_key="client-one")
    second = Client(api_key="client-two")
    first_sent = capture_requests(monkeypatch, first)
    second_sent = capture_requests(monkeypatch, second)
    params = dict(PARAMS[method])
    if explicit_key:
        params["api_key"] = "caller-key"
    original = copy.deepcopy(params)
    getattr(first, method)(params)
    getattr(second, method)(params)
    expected = ["caller-key", "caller-key"] if explicit_key else ["client-one", "client-two"]
    actual = [parse_qs(urlsplit(sent[0].url).query)["api_key"][0] for sent in (first_sent, second_sent)]
    assert actual == expected
    assert params == original


@pytest.mark.parametrize("method,override", [
    ("search", {"q": "tea"}),
    ("search_archive", {"output": "json"}),
    ("locations", {"limit": 2}),
    ("account", {"api_key": "caller-key"}),
])
def test_keyword_overrides_do_not_mutate_params(monkeypatch, method, override):
    client = Client(api_key="client-key")
    sent = capture_requests(monkeypatch, client)
    params = dict(PARAMS[method])
    original = copy.deepcopy(params)
    client.session.trust_env = False
    options = dict(timeout=4, verify="ca.pem", cert="client.pem", stream=True,
                   proxies={"https": "http://proxy.invalid"})
    with patch.object(client.session, "send", wraps=client.session.send) as send:
        getattr(client, method)(params, **override, **options)
    assert all(send.call_args[1][key] == value for key, value in options.items())
    query = parse_qs(urlsplit(sent[0].url).query)
    assert set(options).isdisjoint(query)
    for key, value in override.items():
        assert query[key] == [str(value)]
    assert params == original


@pytest.mark.parametrize("explicit_key", [False, True])
def test_direct_request_does_not_mutate_params(monkeypatch, explicit_key):
    client = Client(api_key="client-key")
    sent = capture_requests(monkeypatch, client)
    params = {"api_key": "caller-key"} if explicit_key else {}
    original = dict(params)
    client.request("GET", "/search", params)
    assert parse_qs(urlsplit(sent[0].url).query)["api_key"] == ["caller-key" if explicit_key else "client-key"]
    assert params == original


def test_session_wrapper_without_params(monkeypatch):
    client = Client(api_key="client-key")
    sent = capture_requests(monkeypatch, client)
    client.session = SimpleNamespace(request=client.session.request)

    client.search(q="coffee")

    assert parse_qs(urlsplit(sent[0].url).query) == {"q": ["coffee"], "api_key": ["client-key"]}


def test_form_key_preserves_repeated_query_fields(monkeypatch):
    client = Client(api_key="client-key")
    sent = capture_requests(monkeypatch, client)
    client.request("POST", "/example", [("tag", "coffee"), ("tag", "tea")],
                   data={"api_key": "form-key"})
    assert parse_qs(urlsplit(sent[0].url).query) == {"tag": ["coffee", "tea"]}


@pytest.mark.parametrize("constructor,overrides,expected", [
    (None, {}, ["session-key"]),
    ("client-key", {}, ["client-key"]),
    ("client-key", {"api_key": "caller-key"}, ["caller-key"]),
    ("client-key", {"api_key": None}, []),
    (None, {b"api_key": "caller-key"}, ["caller-key"]),
    (None, {b"api_key": None}, []),
])
def test_query_key_precedence(monkeypatch, constructor, overrides, expected):
    client = Client(api_key=constructor)
    client.session.params = {"api_key": "session-key"}
    sent = capture_requests(monkeypatch, client)
    params = dict(overrides, q="coffee")
    original = params.copy()
    client.search(params)
    assert parse_qs(urlsplit(sent[0].url).query).get("api_key", []) == expected
    assert params == original
    assert client.session.params == {"api_key": "session-key"}


@pytest.mark.parametrize("data", [
    UserDict({"api_key": "form-key"}), [(b"api_key", "form-key")],
])
def test_form_key_suppresses_only_session_key(monkeypatch, data):
    client = Client()
    client.session.params = {"api_key": "session-key", "hl": "en"}
    sent = capture_requests(monkeypatch, client)
    client.request("POST", "/example", {}, data=data)
    assert parse_qs(urlsplit(sent[0].url).query) == {"hl": ["en"]}
    assert parse_qs(sent[0].body) == {"api_key": ["form-key"]}
    assert client.session.params == {"api_key": "session-key", "hl": "en"}


@pytest.mark.parametrize("constructor,overrides,query_keys,form_key", [
    (None, {}, ["session-key"], None),
    ("client-key", {}, [], "client-key"),
    (None, {"api_key": "form-key"}, [], "form-key"),
    ("client-key", {"api_key": None}, [], None),
])
def test_upload_key_precedence(monkeypatch, constructor, overrides, query_keys, form_key):
    client = Client(api_key=constructor)
    client.session.params = {"api_key": "session-key"}
    sent = capture_requests(monkeypatch, client)
    client.upload_image(BytesIO(b"image"), **overrides)
    assert parse_qs(urlsplit(sent[0].url).query).get("api_key", []) == query_keys
    if form_key is None:
        assert b'name="api_key"' not in sent[0].body
    else:
        assert b'name="api_key"\r\n\r\n' + form_key.encode() + b'\r\n' in sent[0].body
