import io
import json
from collections import deque
from pathlib import Path
import subprocess
from types import SimpleNamespace
from urllib.error import HTTPError

import pytest

from scripts import check_docs_revision as guard
from scripts import publish_docs as publisher


COMMIT = "a" * 40
TOKEN = "private-test-token"


def ci_environment(**context_changes):
    context = {"commit": COMMIT, "versions": ["latest"], "expires_at": 200}
    context.update(context_changes)
    return {
        "READTHEDOCS_VERSION": "latest",
        "READTHEDOCS_VERSION_NAME": "latest",
        "READTHEDOCS_VERSION_TYPE": "branch",
        guard.CONTEXT_VARIABLE: json.dumps(context),
    }


def test_revision_guard_accepts_only_the_tested_commit():
    guard.check_revision(ci_environment(), COMMIT, now=100)
    with pytest.raises(RuntimeError, match="different commit"):
        guard.check_revision(ci_environment(), "b" * 40, now=100)


@pytest.mark.parametrize("context", [None, "not json", "null", "[]", "{}"])
def test_revision_guard_rejects_missing_or_malformed_context(context):
    env = ci_environment()
    if context is None:
        env.pop(guard.CONTEXT_VARIABLE)
    else:
        env[guard.CONTEXT_VARIABLE] = context
    with pytest.raises(RuntimeError, match="No valid CI revision"):
        guard.check_revision(env, COMMIT, now=100)


def test_revision_guard_rejects_expired_and_other_versions():
    with pytest.raises(RuntimeError, match="expired"):
        guard.check_revision(ci_environment(expires_at=100), COMMIT, now=100)
    with pytest.raises(RuntimeError, match="did not request"):
        guard.check_revision(ci_environment(versions=["v1.2.3", "stable"]), COMMIT, now=100)


def test_revision_guard_uses_tag_name_instead_of_normalized_slug():
    env = ci_environment(versions=["v1.2.3", "stable"])
    env.update(READTHEDOCS_VERSION="v123", READTHEDOCS_VERSION_NAME="v1.2.3",
               READTHEDOCS_VERSION_TYPE="tag")
    guard.check_revision(env, COMMIT, now=100)
    env["READTHEDOCS_VERSION_NAME"] = "stable"
    guard.check_revision(env, COMMIT, now=100)
    env["READTHEDOCS_VERSION"] = "stable"
    env["READTHEDOCS_VERSION_NAME"] = "v9.0.0"
    with pytest.raises(RuntimeError, match="did not request"):
        guard.check_revision(env, COMMIT, now=100)


def test_revision_guard_falls_back_to_slug_when_name_is_missing():
    env = ci_environment()
    env.pop("READTHEDOCS_VERSION_NAME")
    guard.check_revision(env, COMMIT, now=100)


def test_pr_preview_needs_no_ci_context():
    guard.check_revision({"READTHEDOCS_VERSION_TYPE": "external"}, COMMIT)


def page(*items, next=None):
    return {"results": list(items), "next": next}


def build(build_id=10, **changes):
    result = {
        "id": build_id, "version": "latest", "commit": COMMIT,
        "state": {"code": "finished"}, "success": True,
    }
    result.update(changes)
    return result


class HTTPResponses:
    # Route requests by endpoint; successive responses model asynchronous changes.
    def __init__(self):
        self.routes = {}
        self.requests = []

    def respond(self, method, path, *responses):
        self.routes[method, path] = deque(responses)

    def open(self, request, timeout):
        assert request.get_header("Authorization") == f"Token {TOKEN}"
        assert request.get_header("Content-type") == "application/json"
        assert TOKEN not in request.full_url
        assert timeout > 0
        base = f"{publisher.API_ROOT}projects/{publisher.PROJECT}/"
        assert request.full_url.startswith(base)
        path = request.full_url[len(base):]
        data = json.loads(request.data) if request.data is not None else None
        self.requests.append((request.get_method(), path, data))
        responses = self.routes[request.get_method(), path]
        response = responses.popleft() if len(responses) > 1 else responses[0]
        if isinstance(response, Exception):
            raise response
        if not isinstance(response, bytes):
            response = b"" if response is None else json.dumps(response).encode()
        return io.BytesIO(response)

    def sent(self, method, path):
        return [data for verb, endpoint, data in self.requests
                if (verb, endpoint) == (method, path)]


@pytest.fixture
def clock(monkeypatch):
    clock = SimpleNamespace(elapsed=0)

    def sleep(seconds):
        clock.elapsed += seconds

    monkeypatch.setattr(publisher, "time", SimpleNamespace(
        time=lambda: 100, monotonic=lambda: clock.elapsed, sleep=sleep,
    ))
    return clock


@pytest.fixture
def rtd(monkeypatch, clock):
    rtd = HTTPResponses()
    rtd.respond("GET", "", {"default_branch": "master"})
    rtd.respond("GET", "builds/?running=true", page())
    rtd.respond("GET", "environmentvariables/", page({"name": "UNRELATED", "pk": 1}))
    rtd.respond("GET", "builds/?limit=1", page(build(9)))
    rtd.respond("POST", "environmentvariables/", {"pk": 2})
    rtd.respond("POST", "sync-versions/", {})
    rtd.respond("GET", "versions/latest/", {"slug": "latest", "active": True})
    rtd.respond("GET", "builds/", page(build(9)))
    rtd.respond("POST", "versions/latest/builds/", {"build": build()})
    rtd.respond("GET", "builds/10/", build())
    rtd.respond("DELETE", "environmentvariables/2/", None)
    monkeypatch.setattr(publisher, "build_opener", lambda *handlers: SimpleNamespace(open=rtd.open))
    rtd.api = publisher.ReadTheDocs(TOKEN)
    return rtd


@pytest.fixture
def github_run(monkeypatch, rtd):
    monkeypatch.chdir(Path(__file__).resolve().parents[1])
    commit = subprocess.check_output(["git", "rev-parse", "HEAD"], text=True).strip()
    for name, value in {
        "RTD_API_TOKEN": TOKEN, "GITHUB_EVENT_NAME": "push",
        "GITHUB_SHA": commit, "GITHUB_REF": "refs/heads/master",
    }.items():
        monkeypatch.setenv(name, value)
    rtd.respond("GET", "builds/10/", build(commit=commit))
    return commit


@pytest.mark.parametrize("event", ["push", "workflow_dispatch"])
def test_main_publishes_the_checkout_with_scoped_context_and_cleanup(monkeypatch, rtd, github_run, event):
    monkeypatch.setenv("GITHUB_EVENT_NAME", event)
    publisher.main()
    creation, = rtd.sent("POST", "environmentvariables/")
    assert creation["public"] is False
    assert creation["name"] == guard.CONTEXT_VARIABLE
    context = json.loads(creation["value"])
    assert context["commit"] == github_run
    assert context["versions"] == ["latest"]
    assert context["expires_at"] > publisher.time.time()
    assert rtd.sent("DELETE", "environmentvariables/2/") == [None]
    actions = [(method, path) for method, path, _ in rtd.requests]
    assert (actions.index(("POST", "environmentvariables/"))
            < actions.index(("POST", "sync-versions/"))
            < actions.index(("POST", "versions/latest/builds/"))
            < actions.index(("DELETE", "environmentvariables/2/")))


@pytest.mark.parametrize("name, value, message", [
    ("RTD_API_TOKEN", None, "Add RTD_API_TOKEN"),
    ("GITHUB_EVENT_NAME", "pull_request", "PR runs cannot publish"),
    ("GITHUB_SHA", "0" * 40, "checkout does not match"),
])
def test_main_rejects_invalid_ci_environment_before_contacting_rtd(monkeypatch, rtd, github_run, name, value, message):
    if value is None:
        monkeypatch.delenv(name)
    else:
        monkeypatch.setenv(name, value)
    with pytest.raises(RuntimeError, match=message):
        publisher.main()
    assert not rtd.requests


@pytest.mark.parametrize("stable_ref", ["v1.2.3", "v2.0.0", None])
def test_release_discovers_and_activates_tag_then_publishes_matching_stable(rtd, clock, stable_ref):
    tag = {"slug": "v123", "active": False}
    rtd.respond("GET", "versions/?type=tag&verbose_name=v1.2.3", page(), page(tag))
    rtd.respond("PATCH", "versions/v123/", None)
    rtd.respond("GET", "builds/", page(build(9)), page(build(9)),
                page(build(version="v123")))
    rtd.respond("GET", "builds/10/", build(state={"code": "building"}, success=None),
                build(version="v123"))
    stable = ({"slug": "stable", "active": True, "ref": stable_ref}
              if stable_ref else HTTPError(rtd.api.base + "versions/stable/", 404, "Not found", {}, None))
    rtd.respond("GET", "versions/stable/", stable)
    rtd.respond("POST", "versions/stable/builds/", {"build": build(11, version="stable")})
    rtd.respond("GET", "builds/11/", build(11, version="stable"))

    publisher.publish(rtd.api, "refs/tags/v1.2.3", COMMIT)

    assert clock.elapsed > 0
    assert rtd.sent("PATCH", "versions/v123/") == [{"active": True, "hidden": False}]
    assert not rtd.sent("POST", "versions/v123/builds/")
    assert len(rtd.sent("POST", "versions/stable/builds/")) == (stable_ref == "v1.2.3")
    creation, = rtd.sent("POST", "environmentvariables/")
    assert json.loads(creation["value"])["versions"] == ["v1.2.3", "stable"]
    assert rtd.sent("DELETE", "environmentvariables/2/") == [None]


def test_publisher_reuses_matching_build_started_by_sync(rtd):
    rtd.respond("GET", "builds/", page(build(11, version="v123"), build(10, version="stable")))
    rtd.respond("GET", "builds/10/", build(version="stable"))
    result = publisher.publish_version(rtd.api, {"slug": "stable", "active": True}, COMMIT, after=9)
    assert result["id"] == 10
    assert all(method == "GET" for method, _, _ in rtd.requests)


@pytest.mark.parametrize("outcome, message", [
    (build(success=False), "failed or was cancelled"),
    (build(state={"code": "cancelled"}, success=None), "failed or was cancelled"),
    (build(commit="b" * 40), "different commit"),
    (build(state={"code": "building"}, success=None), "Timed out waiting"),
])
def test_failed_or_stalled_publication_removes_context(rtd, outcome, message):
    rtd.respond("GET", "builds/10/", outcome)
    with pytest.raises(RuntimeError, match=message):
        publisher.publish(rtd.api, "refs/heads/master", COMMIT)
    assert len(rtd.sent("POST", "environmentvariables/")) == 1
    assert rtd.sent("DELETE", "environmentvariables/2/") == [None]


def test_publisher_waits_for_existing_builds_before_changing_context(rtd):
    rtd.respond("GET", "builds/?running=true", page(build()), page())
    publisher.publish(rtd.api, "refs/heads/master", COMMIT)
    actions = [(method, path) for method, path, _ in rtd.requests]
    polls = [index for index, action in enumerate(actions) if action == ("GET", "builds/?running=true")]
    assert len(polls) >= 2
    assert max(polls) < actions.index(("POST", "environmentvariables/"))


def test_context_cleanup_follows_pagination_and_preserves_other_variables(rtd):
    next_url = rtd.api.base + "environmentvariables/?offset=1"
    rtd.respond("GET", "environmentvariables/", page({"name": "UNRELATED", "pk": 1}, next=next_url))
    rtd.respond("GET", "environmentvariables/?offset=1", page({"name": guard.CONTEXT_VARIABLE, "pk": 2}))
    publisher.clear_context(rtd.api)
    assert [(path, data) for method, path, data in rtd.requests if method == "DELETE"] == [
        ("environmentvariables/2/", None),
    ]


def test_api_keeps_token_out_of_errors_and_rejects_external_urls(rtd):
    rtd.respond("GET", "", HTTPError(rtd.api.base, 403, TOKEN, {}, io.BytesIO(TOKEN.encode())))
    with pytest.raises(publisher.APIError) as failure:
        rtd.api.request("GET", "")
    assert TOKEN not in str(failure.value)
    assert failure.value.status == 403
    with pytest.raises(RuntimeError, match="outside"):
        rtd.api.request("GET", "https://example.com/")


def test_api_reports_invalid_json_response(rtd):
    rtd.respond("GET", "", b"<html>Service unavailable</html>")
    with pytest.raises(RuntimeError, match="invalid API response"):
        rtd.api.request("GET", "")


@pytest.mark.parametrize("ref", ["refs/heads/feature", "refs/pull/1/merge", "refs/tags/test"])
def test_publisher_rejects_refs_outside_release_policy(rtd, ref):
    with pytest.raises(RuntimeError, match="Only master"):
        publisher.publish(rtd.api, ref, COMMIT)
    assert not rtd.requests
