import json
import os
import re
import subprocess
import sys
import time


CONTEXT_VARIABLE = "DOCS_CI_REVISION"


def check_revision(environ, commit, now=None):
    if environ.get("READTHEDOCS_VERSION_TYPE") == "external":
        return
    try:
        context = json.loads(environ[CONTEXT_VARIABLE])
        expected = context["commit"]
        versions = context["versions"]
        expires = context["expires_at"]
        if not re.fullmatch(r"[0-9a-f]{40}", expected):
            raise ValueError
        if not isinstance(versions, list) or not versions:
            raise ValueError
        if not isinstance(expires, (int, float)):
            raise ValueError
    except (KeyError, TypeError, ValueError):
        raise RuntimeError(
            "No valid CI revision was supplied. Publish through the Documentation workflow."
        ) from None
    if (time.time() if now is None else now) >= expires:
        raise RuntimeError("The CI revision expired. Rerun the Documentation workflow.")
    name = environ.get("READTHEDOCS_VERSION_NAME") or environ.get("READTHEDOCS_VERSION")
    if name not in versions:
        raise RuntimeError("CI did not request publication of this documentation version.")
    if commit != expected:
        raise RuntimeError(
            "RTD checked out a different commit than the one tested by CI. "
            "Rerun the Documentation workflow on the current branch or tag."
        )


def main():
    commit = subprocess.check_output(["git", "rev-parse", "HEAD"], text=True).strip()
    check_revision(os.environ, commit)
    print("Documentation revision check passed.")


if __name__ == "__main__":
    try:
        main()
    except RuntimeError as exc:
        print(str(exc), file=sys.stderr)
        sys.exit(1)
