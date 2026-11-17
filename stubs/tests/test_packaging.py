import os
import re
import subprocess
import textwrap
from pathlib import Path

import pytest

STUBS_ROOT = Path(__file__).resolve().parent.parent


def test_license_matches_the_sdk_license():
    assert (STUBS_ROOT / "LICENSE").read_bytes() == (STUBS_ROOT.parent / "LICENSE").read_bytes()


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


@pytest.mark.parametrize("maintainer, regenerated", [(True, False), (True, True), (False, False)])
def test_refresh_preserves_maintainer_prs(tmp_path, git_repo, maintainer, regenerated):
    workflow = (STUBS_ROOT.parent / ".github" / "workflows" / "stubs-refresh.yml").read_text(encoding="utf-8")
    script = textwrap.dedent(workflow.rsplit("        run: |\n", 1)[1])
    script = script.replace("${{ github.event.repository.default_branch }}", "master")
    calls = tmp_path / "gh-calls"
    repo, env, git = git_repo
    env.update(BRANCH="bot/refresh-serpapi-stubs", GH_CALLS=str(calls))
    (repo / "stubs").mkdir()
    stub = repo / "stubs" / "example.pyi"
    stub.write_text("original\n", encoding="utf-8")
    git("add", "stubs")
    git("commit", "--quiet", "-m", "Base")
    git("switch", "--quiet", "-c", env["BRANCH"])
    if maintainer:
        env["GIT_AUTHOR_NAME"] = env["GIT_COMMITTER_NAME"] = "Maintainer"
    stub.write_text("reviewed correction\n", encoding="utf-8")
    git("commit", "--quiet", "-am", "Correct stubs")
    tip = git("rev-parse", "HEAD")
    git("switch", "--quiet", "master")
    git("remote", "add", "origin", str(repo))
    if regenerated:
        stub.write_text("new generated metadata\n", encoding="utf-8")

    # Stub only GitHub calls; all branch inspection uses a real, local Git repository.
    gh = """
gh() {
  printf '%s\\n' "$*" >> "$GH_CALLS"
  if [ "$1 $2" = "pr list" ]; then printf '42\\n'; fi
}
"""
    result = subprocess.run(
        ["bash", "-e", "-c", gh + script], cwd=repo, env=env, capture_output=True, text=True
    )
    assert result.returncode == 0, result.stderr
    commands = calls.read_text(encoding="utf-8").splitlines()
    assert git("rev-parse", env["BRANCH"]) == tip
    if maintainer:
        assert len(commands) == 1, commands
        assert "left unchanged" in result.stdout
    else:
        assert any(command.startswith("pr close 42 ") and "--delete-branch" in command for command in commands)


@pytest.mark.parametrize(
    ("changes", "publish"),
    [
        ([], True),
        ([(None, "unreleased")], True),
        ([("future", "unreleased")], True),
        ([("corrected", None)], False),
        ([("corrected", None), ("future", "unreleased")], False),
        ([("corrected", None), ("original", "unreleased")], False),
    ],
)
@pytest.mark.parametrize("branch", ["master", "stubs/hotfix-1.2.0"])
def test_release_only_skips_for_newer_compatible_stubs(tmp_path, git_repo, changes, publish, branch):
    workflow = (STUBS_ROOT.parent / ".github" / "workflows" / "stubs-release.yml").read_text(encoding="utf-8")
    step = workflow.split("      - id: current\n", 1)[1]
    script = textwrap.dedent(step.split("        run: |\n", 1)[1].split("\n      - uses:", 1)[0])
    repo, env, git = git_repo
    output = tmp_path / "github_output"
    env.update(GITHUB_REF_NAME=branch, GITHUB_OUTPUT=str(output))
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
        git("commit", "--quiet", "-am", "Next change")
    git("remote", "add", "origin", str(repo))
    git("switch", "--quiet", "--detach", running_commit)

    result = subprocess.run(
        ["bash", "-e", "-c", script], cwd=repo, env=env, capture_output=True, text=True
    )
    assert result.returncode == 0, result.stderr
    assert output.read_text(encoding="utf-8") == f"publish={str(publish).lower()}\n"
