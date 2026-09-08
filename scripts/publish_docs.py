import json
import os
import re
import subprocess
import sys
import time
from urllib.error import HTTPError, URLError
from urllib.parse import quote, urlencode, urljoin
from urllib.request import HTTPRedirectHandler, Request, build_opener

from scripts.check_docs_revision import CONTEXT_VARIABLE


PROJECT = "serpapi-python"
API_ROOT = "https://app.readthedocs.org/api/v3/"
POLL_SECONDS = 10
BUILD_TIMEOUT = 1200


class APIError(RuntimeError):
    def __init__(self, status):
        self.status = status
        super().__init__(f"Read the Docs API returned HTTP {status}.")


class NoRedirect(HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        return None


class ReadTheDocs:
    def __init__(self, token):
        self.token = token
        self.base = f"{API_ROOT}projects/{PROJECT}/"
        self.open = build_opener(NoRedirect()).open

    def request(self, method, path, data=None):
        url = urljoin(self.base, path)
        if not url.startswith(self.base):
            raise RuntimeError("Refusing to send the RTD token outside this project's API.")
        body = None if data is None else json.dumps(data).encode()
        request = Request(url, data=body, method=method, headers={
            "Authorization": f"Token {self.token}",
            "Content-Type": "application/json",
            "User-Agent": "serpapi-python-docs-publisher",
        })
        try:
            with self.open(request, timeout=30) as response:
                payload = response.read()
        except HTTPError as exc:
            raise APIError(exc.code) from None
        except (URLError, TimeoutError):
            raise RuntimeError("Could not reach the Read the Docs API.") from None
        try:
            return json.loads(payload) if payload else None
        except ValueError:
            raise RuntimeError("Read the Docs returned an invalid API response.") from None

    def items(self, path):
        while path:
            page = self.request("GET", path)
            yield from page["results"]
            path = page.get("next")


def wait_for(check, message, timeout=BUILD_TIMEOUT):
    deadline = time.monotonic() + timeout
    while True:
        result = check()
        if result:
            return result
        if time.monotonic() >= deadline:
            raise RuntimeError(message)
        time.sleep(POLL_SECONDS)


def version_path(slug):
    return f"versions/{quote(slug, safe='')}/"


def find_version(api, ref):
    if ref == "refs/heads/master":
        return api.request("GET", version_path("latest"))
    query = urlencode({"type": "tag", "verbose_name": ref[len("refs/tags/"):]})
    versions = list(api.items(f"versions/?{query}"))
    if len(versions) > 1:
        raise RuntimeError("More than one RTD version matches the release tag.")
    return versions[0] if versions else None


def wait_for_build(api, build, commit):
    build_id = build["id"]
    url = f"https://app.readthedocs.org/projects/{PROJECT}/builds/{build_id}/"
    print(f"Waiting for RTD build: {url}", flush=True)

    def finished():
        current = api.request("GET", f"builds/{build_id}/")
        state = current["state"]["code"]
        if state not in ("finished", "cancelled"):
            return None
        if not current.get("success"):
            raise RuntimeError(f"RTD build failed or was cancelled. See {url}")
        if current.get("commit") != commit:
            raise RuntimeError(f"RTD built a different commit. See {url}")
        return current

    return wait_for(finished, f"Timed out waiting for RTD. See {url}")


def newest_build(api, version, after):
    for build in api.items("builds/"):
        if build["id"] <= after:
            break
        if build["version"] == version:
            return build
    return None


def publish_version(api, version, commit, after=None):
    path = version_path(version["slug"])
    # Syncing versions can queue stable and release builds without an automation rule.
    build = newest_build(api, version["slug"], after) if after is not None else None
    if build:
        return wait_for_build(api, build, commit)
    if not version["active"]:
        previous = api.request("GET", "builds/?limit=1")["results"]
        last_id = previous[0]["id"] if previous else 0
        # Activating a version already queues a build; do not queue a second one.
        api.request("PATCH", path, {"active": True, "hidden": False})

        def activated_build():
            return newest_build(api, version["slug"], last_id)

        build = wait_for(activated_build, "RTD did not queue the activated version.", 120)
    else:
        build = api.request("POST", path + "builds/")["build"]
    return wait_for_build(api, build, commit)


def clear_context(api):
    for variable in list(api.items("environmentvariables/")):
        if variable["name"] == CONTEXT_VARIABLE:
            api.request("DELETE", f"environmentvariables/{variable['pk']}/")


def publish(api, ref, commit):
    if ref != "refs/heads/master" and not ref.startswith("refs/tags/v"):
        raise RuntimeError("Only master and v-prefixed release tags can publish documentation.")
    if not re.fullmatch(r"[0-9a-f]{40}", commit):
        raise RuntimeError("Expected a full Git commit hash.")
    project = api.request("GET", "")
    if project["default_branch"] != "master":
        raise RuntimeError("Set the RTD project's Default branch to master first.")

    # Serialize in Actions, and let any previous RTD build finish before changing its context.
    wait_for(
        lambda: not api.request("GET", "builds/?running=true")["results"],
        "Existing RTD builds did not finish. Check the RTD dashboard before retrying.",
    )
    clear_context(api)
    previous = api.request("GET", "builds/?limit=1")["results"]
    last_id = previous[0]["id"] if previous else 0
    versions = ["latest"] if ref == "refs/heads/master" else [ref[len("refs/tags/"):], "stable"]
    context = {
        "commit": commit,
        "versions": versions,
        "expires_at": time.time() + 3600,
    }
    variable = api.request("POST", "environmentvariables/", {
        "name": CONTEXT_VARIABLE, "value": json.dumps(context), "public": False,
    })
    try:
        api.request("POST", "sync-versions/")
        version = wait_for(lambda: find_version(api, ref), "RTD did not discover the Git tag.", 120)
        publish_version(api, version, commit, after=last_id)
        if ref.startswith("refs/tags/"):
            try:
                stable = api.request("GET", version_path("stable"))
            except APIError as exc:
                if exc.status != 404:
                    raise
                stable = None
            if stable and stable.get("ref") == ref[len("refs/tags/"):]:
                publish_version(api, stable, commit, after=last_id)
        print(f"Published documentation for {ref} at {commit}.", flush=True)
    finally:
        api.request("DELETE", f"environmentvariables/{variable['pk']}/")


def main():
    token = os.environ.get("RTD_API_TOKEN")
    if not token:
        raise RuntimeError("Add RTD_API_TOKEN to the docs GitHub environment before publishing.")
    if os.environ.get("GITHUB_EVENT_NAME") not in ("push", "workflow_dispatch"):
        raise RuntimeError("PR runs cannot publish documentation.")
    commit = subprocess.check_output(["git", "rev-parse", "HEAD"], text=True).strip()
    if commit != os.environ.get("GITHUB_SHA"):
        raise RuntimeError("The publishing checkout does not match the commit tested by CI.")
    publish(ReadTheDocs(token), os.environ.get("GITHUB_REF", ""), commit)


if __name__ == "__main__":
    try:
        main()
    except RuntimeError as exc:
        print(str(exc), file=sys.stderr)
        sys.exit(1)
