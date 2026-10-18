import copy
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
    getattr(client, method)(params, **override)
    query = parse_qs(urlsplit(sent[0].url).query)
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
