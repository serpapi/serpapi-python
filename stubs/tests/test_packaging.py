import os
import re
import subprocess
import textwrap
from pathlib import Path

import pytest
from packaging.requirements import Requirement
from packaging.version import Version

from release_version import FINAL_RELEASE, read_sdk_version

STUBS_ROOT = Path(__file__).resolve().parent.parent


def test_license_matches_the_sdk_license():
    assert (STUBS_ROOT / "LICENSE").read_bytes() == (STUBS_ROOT.parent / "LICENSE").read_bytes()


def test_stubs_declare_their_supported_sdk_range():
    import tomllib

    project = tomllib.loads((STUBS_ROOT / "pyproject.toml").read_text())["project"]
    sdk, = (req for req in map(Requirement, project["dependencies"]) if req.name == "serpapi")
    current = Version(read_sdk_version())
    raw_floor, = (spec.version for spec in sdk.specifier if spec.operator == ">=")
    floor = Version(raw_floor)
    assert FINAL_RELEASE.fullmatch(raw_floor) and raw_floor == str(floor), (
        f"Use the full SDK tag version X.Y.Z without leading zeros, not {raw_floor!r}"
    )
    assert floor.major == current.major
    assert current in sdk.specifier
    assert sdk == Requirement(f"serpapi>={floor},<{current.major + 1}")


def test_release_compares_every_path_that_starts_it():
    # The stale-run check in stubs-release.yml must cover the same shipped files as the push trigger.
    workflow = (STUBS_ROOT.parent / ".github" / "workflows" / "stubs-release.yml").read_text(encoding="utf-8")
    trigger = {path.replace("/**", "") for path in re.findall(r'^ +- "(stubs/[^"]+)"$', workflow, re.MULTILINE)}
    compared = re.search(r"stub_paths=\(\s*(.*?)\s*\)", workflow, re.DOTALL).group(1).split()
    assert trigger and trigger == set(compared)


@pytest.fixture
def git_repo(tmp_path):
    repo = tmp_path / "repo"
    repo.mkdir()
    env = {
        **os.environ,
        "GIT_CONFIG_GLOBAL": os.devnull,
        "GIT_CONFIG_NOSYSTEM": "1",
        "GIT_AUTHOR_NAME": "github-actions[bot]",
        "GIT_COMMITTER_NAME": "github-actions[bot]",
        "GIT_AUTHOR_EMAIL": "bot@example.com",
        "GIT_COMMITTER_EMAIL": "bot@example.com",
    }

    def git(*args):
        return subprocess.run(
            ["git", *args], cwd=repo, env=env, check=True, capture_output=True, text=True
        ).stdout.strip()

    git("init", "--quiet", "--initial-branch=master")
    return repo, env, git


@pytest.mark.parametrize("correction, regenerated", [("before_fetch", False), ("before_fetch", True), ("after_fetch", False), (None, False)])
@pytest.mark.parametrize("bot_followup", [False, True])
def test_refresh_preserves_maintainer_prs(tmp_path, git_repo, correction, regenerated, bot_followup):
    workflow = (STUBS_ROOT.parent / ".github" / "workflows" / "stubs-refresh.yml").read_text(encoding="utf-8")
    script = textwrap.dedent(workflow.rsplit("        run: |\n", 1)[1])
    script = script.replace("${{ github.event.repository.default_branch }}", "master")
    calls = tmp_path / "gh-calls"
    repo, env, git = git_repo
    env.update(BRANCH="bot/refresh-serpapi-stubs", GH_CALLS=str(calls), LATE_TIP="")
    (repo / "stubs").mkdir()
    stub = repo / "stubs" / "example.pyi"
    stub.write_text("original\n", encoding="utf-8")
    git("add", "stubs")
    git("commit", "--quiet", "-m", "Base")
    git("switch", "--quiet", "-c", env["BRANCH"])
    if correction == "before_fetch":
        env["GIT_AUTHOR_NAME"] = env["GIT_COMMITTER_NAME"] = "Maintainer"
    stub.write_text("reviewed correction\n", encoding="utf-8")
    git("commit", "--quiet", "-am", "Correct stubs")
    if bot_followup:
        env["GIT_AUTHOR_NAME"] = env["GIT_COMMITTER_NAME"] = "github-actions[bot]"
        stub.write_text("reviewed correction\nbot followup\n", encoding="utf-8")
        git("commit", "--quiet", "-am", "Bot followup")
    tip = git("rev-parse", "HEAD")
    if correction == "after_fetch":
        # Prepare a real correction without moving the remote branch until the workflow has fetched it.
        git("switch", "--quiet", "--detach", tip)
        env["GIT_AUTHOR_NAME"] = env["GIT_COMMITTER_NAME"] = "Maintainer"
        stub.write_text("concurrent maintainer correction\n", encoding="utf-8")
        git("commit", "--quiet", "-am", "Concurrent correction")
        env["LATE_TIP"] = git("rev-parse", "HEAD")
    git("switch", "--quiet", "master")
    git("remote", "add", "origin", str(repo))
    if regenerated:
        stub.write_text("new generated metadata\n", encoding="utf-8")

    prelude = """
git() {
  command git "$@" || return
  if [ "$1" = fetch ] && [ -n "$LATE_TIP" ]; then
    command git update-ref "refs/heads/$BRANCH" "$LATE_TIP" FETCH_HEAD
  fi
}
gh() {
  printf '%s\\n' "$*" >> "$GH_CALLS"
  if [ "$1 $2" = "pr list" ]; then printf '42\\n'; fi
}
"""
    result = subprocess.run(
        ["bash", "-e", "-c", prelude + script], cwd=repo, env=env, capture_output=True, text=True
    )
    commands = calls.read_text(encoding="utf-8").splitlines()
    if correction == "after_fetch":
        assert len(commands) == 1, commands  # Only the initial PR lookup; no close or comment.
        assert git("rev-parse", env["BRANCH"]) == env["LATE_TIP"]
        assert result.returncode != 0, result.stdout
        return
    assert result.returncode == 0, result.stderr
    if correction == "before_fetch":
        assert git("rev-parse", env["BRANCH"]) == tip
        assert len(commands) == 1, commands
        assert "left unchanged" in result.stdout
    else:
        assert not git("ls-remote", "origin", f"refs/heads/{env['BRANCH']}")
        assert "pr close 42" in commands
        assert any(command.startswith("pr comment 42 --body ") for command in commands)


@pytest.mark.parametrize(
    ("changes", "run_lookup", "publish"),
    [
        ([], "missing", True),
        ([(None, "unreleased")], "missing", True),
        ([("future", "unreleased")], "missing", True),
        ([("corrected", None)], "found", False),
        ([("corrected", None), ("future", "unreleased")], "found", False),
        ([("corrected", None), ("original", "unreleased")], "found", False),
        ([("corrected", None)], "missing", True),
        ([("corrected", None), ("future", "unreleased")], "missing", True),
        ([("corrected", None)], "error", None),
        ([("corrected", None), (None, None)], "tip", False),
        ([(None, None)], "tip", True),
    ],
)
@pytest.mark.parametrize("branch", ["master", "stubs/hotfix-1.2.0"])
def test_release_only_skips_for_newer_compatible_stubs(tmp_path, git_repo, changes, run_lookup, publish, branch):
    workflow = (STUBS_ROOT.parent / ".github" / "workflows" / "stubs-release.yml").read_text(encoding="utf-8")
    step = workflow.split("      - id: current\n", 1)[1]
    script = textwrap.dedent(step.split("        run: |\n", 1)[1].split("\n      - uses:", 1)[0])
    repo, env, git = git_repo
    output = tmp_path / "github_output"
    calls = tmp_path / "gh-calls"
    env.update(
        GITHUB_REF_NAME=branch, GITHUB_OUTPUT=str(output), GITHUB_REPOSITORY="example/repo",
        RELEASE_RUN=run_lookup, GH_CALLS=str(calls),
    )
    if branch != "master":
        git("switch", "--quiet", "-c", branch)
    (repo / "serpapi").mkdir()
    (repo / "stubs" / "serpapi-stubs").mkdir(parents=True)
    sdk = repo / "serpapi" / "core.py"
    stub = repo / "stubs" / "serpapi-stubs" / "core.pyi"
    sdk.write_text("released\n", encoding="utf-8")
    stub.write_text("original\n", encoding="utf-8")
    git("add", "serpapi", "stubs")
    git("commit", "--quiet", "-m", "Released SDK with stub fix")
    running_commit = git("rev-parse", "HEAD")
    for new_stub, new_sdk in changes:
        if new_stub is not None:
            stub.write_text(new_stub + "\n", encoding="utf-8")
        if new_sdk is not None:
            sdk.write_text(new_sdk + "\n", encoding="utf-8")
        if new_stub is None and new_sdk is None:
            (repo / "CONTRIBUTING.md").write_text("Documentation follow-up\n", encoding="utf-8")
            git("add", "CONTRIBUTING.md")
        git("commit", "--quiet", "-am", "Next change")
    env["RUN_HEAD"] = git("rev-parse", "HEAD")
    git("remote", "add", "origin", str(repo))
    git("switch", "--quiet", "--detach", running_commit)

    gh = """
gh() {
  printf '%s\\n' "$*" >> "$GH_CALLS"
  case "$RELEASE_RUN" in
    found) printf 'https://github.com/example/repo/actions/runs/42\\n' ;;
    tip)
      for arg in "$@"; do
        if [ "$arg" = "head_sha=$RUN_HEAD" ]; then
          printf 'https://github.com/example/repo/actions/runs/42\\n'
        fi
      done
      ;;
    error) printf 'run lookup failed\\n' >&2; return 1 ;;
  esac
}
"""
    result = subprocess.run(
        ["bash", "-e", "-c", gh + script], cwd=repo, env=env, capture_output=True, text=True
    )
    if run_lookup == "error":
        assert result.returncode != 0
        assert "run lookup failed" in result.stderr
        assert not output.exists()
        return
    assert result.returncode == 0, result.stderr
    assert output.read_text(encoding="utf-8") == f"publish={str(publish).lower()}\n"
    if not publish:
        assert "https://github.com/example/repo/actions/runs/42" in result.stdout
    if calls.exists():
        assert f"branch={branch}" in calls.read_text(encoding="utf-8")
