import json

import pytest
import requests

import serpapi
from serpapi import Client
from serpapi.exceptions import HTTPError, TimeoutError


def json_response(payload, status_code=200):
    response = requests.Response()
    response.status_code = status_code
    response._content = json.dumps(payload).encode()
    response.headers["Content-Type"] = "application/json"
    return response


class FakeSerpApi:
    """Answers /search and /searches/<id> requests without any network access.

    Submitting a search returns a "Processing" search whose ID is derived
    from its query. Each archive request for a search pops the next status
    from that search's script in ``statuses``; the last status repeats.
    """

    def __init__(self):
        self.submit_params = []
        self.archive_params = []
        self.statuses = {}
        self.fail_submit_for = set()

    def request(self, method, url, params, headers, **kwargs):
        if "/searches/" in url:
            return self.archive(url.rsplit("/", 1)[-1], params)
        return self.submit(params)

    def submit(self, params):
        self.submit_params.append(dict(params))
        q = params.get("q")
        if q in self.fail_submit_for:
            return json_response({"error": f"Invalid query: {q}"}, status_code=400)
        return json_response(
            {"search_metadata": {"id": f"id-{q}", "status": "Processing"}}
        )

    def archive(self, search_id, params):
        self.archive_params.append(dict(params))
        statuses = self.statuses.get(search_id, ["Success"])
        status = statuses.pop(0) if len(statuses) > 1 else statuses[0]
        payload = {
            "search_metadata": {"id": search_id, "status": status},
            "search_parameters": {"q": search_id[len("id-"):]},
        }
        if status == "Error":
            payload["error"] = "The search failed"
        return json_response(payload)


@pytest.fixture
def fake():
    return FakeSerpApi()


@pytest.fixture
def batch_client(fake, monkeypatch):
    client = Client(api_key="test_key")
    monkeypatch.setattr(client.session, "request", fake.request)
    return client


def test_async_search_all_succeed(batch_client, fake):
    fake.statuses = {
        "id-coffee": ["Success"],
        "id-tea": ["Cached"],
    }

    results = batch_client.async_search(
        [{"engine": "google", "q": "coffee"}, {"engine": "google", "q": "tea"}],
        poll_interval=0,
    )

    assert [r["search_metadata"]["status"] for r in results] == ["Success", "Cached"]
    assert all(isinstance(r, serpapi.SerpResults) for r in results)
    # Every search was submitted as an asynchronous search.
    assert [p["async"] for p in fake.submit_params] == [True, True]


def test_async_search_preserves_input_order(batch_client, fake):
    # "slow" finishes a round after the others, but keeps its position.
    fake.statuses = {
        "id-slow": ["Processing", "Success"],
        "id-fast": ["Success"],
        "id-cached": ["Cached"],
    }

    results = batch_client.async_search(["slow", "fast", "cached"], poll_interval=0)

    assert [r["search_parameters"]["q"] for r in results] == ["slow", "fast", "cached"]


def test_async_search_polls_until_finished(batch_client, fake):
    fake.statuses = {"id-coffee": ["Processing", "Processing", "Success"]}

    results = batch_client.async_search([{"q": "coffee"}], poll_interval=0)

    assert results[0]["search_metadata"]["status"] == "Success"
    assert len(fake.archive_params) == 3


def test_async_search_failed_submit_does_not_sink_the_batch(batch_client, fake):
    fake.fail_submit_for = {"bad"}

    results = batch_client.async_search(["good", "bad", "also good"], poll_interval=0)

    assert isinstance(results[0], serpapi.SerpResults)
    assert isinstance(results[1], HTTPError)
    assert results[1].error == "Invalid query: bad"
    assert isinstance(results[2], serpapi.SerpResults)


def test_async_search_error_status_is_returned(batch_client, fake):
    fake.statuses = {"id-broken": ["Error"]}

    results = batch_client.async_search(["broken"], poll_interval=0)

    assert isinstance(results[0], serpapi.SerpResults)
    assert results[0]["search_metadata"]["status"] == "Error"
    assert results[0]["error"] == "The search failed"


def test_async_search_queries_with_shared_parameters(batch_client, fake):
    # The call shape proposed in the issue: query strings plus shared parameters.
    results = batch_client.async_search(
        queries=["burly", "creator"],
        engine="youtube",
        device="desktop",
        poll_interval=0,
    )

    assert len(results) == 2
    for params, q in zip(fake.submit_params, ["burly", "creator"]):
        assert params["q"] == q
        assert params["engine"] == "youtube"
        assert params["device"] == "desktop"


def test_async_search_archive_requests_send_only_the_search_id(batch_client, fake):
    fake.statuses = {"id-coffee": ["Processing", "Success"]}

    batch_client.async_search(
        [{"engine": "google", "q": "coffee"}], poll_interval=0
    )

    # Reusing the search parameters (such as "q") makes the archive API error.
    assert fake.archive_params == [
        {"search_id": "id-coffee", "api_key": "test_key"},
        {"search_id": "id-coffee", "api_key": "test_key"},
    ]


def test_async_search_unfinished_search_times_out(batch_client, fake):
    fake.statuses = {"id-slow": ["Processing"]}

    results = batch_client.async_search(
        ["slow"], poll_interval=0.01, timeout=0.1
    )

    assert isinstance(results[0], TimeoutError)


def test_async_search_does_not_mutate_the_given_parameters(batch_client):
    params = {"engine": "google", "q": "coffee"}

    batch_client.async_search([params], poll_interval=0)

    assert params == {"engine": "google", "q": "coffee"}


def test_async_search_empty_batch(batch_client):
    assert batch_client.async_search([]) == []


def test_async_search_requires_searches_or_queries(batch_client):
    with pytest.raises(TypeError):
        batch_client.async_search()
