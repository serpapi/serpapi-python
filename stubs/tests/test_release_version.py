import datetime
import io
import json
from urllib.error import HTTPError

import pytest

import release_version

DAY = datetime.date(2026, 1, 2)


@pytest.mark.parametrize(
    ("existing", "expected"),
    [
        (set(), "1.2.0.20260102"),
        ({"1.2.0.20260101"}, "1.2.0.20260102"),
        ({"1.2.0.20260102"}, "1.2.0.20260102.1"),
        ({"1.2.0.20260102", "1.2.0.20260102.1"}, "1.2.0.20260102.2"),
    ],
)
def test_next_version(existing, expected):
    assert release_version.next_version("1.2.0", DAY, existing) == expected


@pytest.mark.parametrize(
    ("existing", "expected"),
    [
        (set(), False),
        ({"1.2.0.20260101"}, True),
        ({"1.2.1.20260102"}, False),
        ({"1.2.0rc1.20260102"}, False),
    ],
)
def test_has_published_series(existing, expected):
    assert release_version.has_published_series("1.2.0", existing) is expected


@pytest.mark.parametrize(
    "version", ["1.3.0b1", "1.2.0.post1", "1.2.0.dev0", "1.2.0+local", "1.2", "1.2.0.1"]
)
def test_read_sdk_version_rejects_non_final_releases(tmp_path, version):
    path = tmp_path / "__version__.py"
    path.write_text(f'__version__ = "{version}"\n')
    with pytest.raises(ValueError, match="not a final X.Y.Z release"):
        release_version.read_sdk_version(path)


def respond_with(payload):
    def urlopen(request, timeout):
        return io.BytesIO(json.dumps(payload).encode())

    return urlopen


def test_published_versions_reads_release_keys(monkeypatch):
    monkeypatch.setattr(
        release_version, "urlopen", respond_with({"releases": {"1.2.0.20260101": [], "1.2.0.20260102": []}})
    )
    assert release_version.published_versions() == {"1.2.0.20260101", "1.2.0.20260102"}


def test_published_versions_fails_on_unexpected_payload(monkeypatch):
    monkeypatch.setattr(release_version, "urlopen", respond_with({"info": {}}))
    with pytest.raises(KeyError):
        release_version.published_versions()


def test_published_versions_treats_missing_project_as_empty(monkeypatch):
    def not_found(request, timeout):
        raise HTTPError(request.full_url, 404, "Not Found", {}, io.BytesIO())

    monkeypatch.setattr(release_version, "urlopen", not_found)
    assert release_version.published_versions() == set()


def test_published_versions_does_not_hide_other_http_errors(monkeypatch):
    def unavailable(request, timeout):
        raise HTTPError(request.full_url, 503, "Service Unavailable", {}, io.BytesIO())

    monkeypatch.setattr(release_version, "urlopen", unavailable)
    with pytest.raises(HTTPError):
        release_version.published_versions()


def test_main_writes_version_file(tmp_path):
    output = tmp_path / "VERSION"

    assert release_version.main(["--offline", "--date", "20260102", "--output", str(output)]) == 0

    assert output.read_text() == f"{release_version.read_sdk_version()}.20260102\n"


@pytest.mark.parametrize(
    ("tag", "existing", "exit_code", "github_output"),
    [
        ("v1.2.0", set(), 0, "publish=true\n"),
        ("v1.2.0", {"1.2.0.20260101"}, 0, "publish=false\n"),
        # A tag that does not name the SDK version must stop the release before anything is uploaded.
        ("v1.2.1", set(), 1, ""),
        ("v1.2.0-rc1", set(), 1, ""),
        ("master", set(), 1, ""),
    ],
)
def test_series_check(tmp_path, monkeypatch, tag, existing, exit_code, github_output):
    output = tmp_path / "github_output"
    output.touch()
    monkeypatch.setenv("GITHUB_OUTPUT", str(output))
    monkeypatch.setattr(release_version, "read_sdk_version", lambda: "1.2.0")
    monkeypatch.setattr(
        release_version, "urlopen", respond_with({"releases": {version: [{"yanked": False}] for version in existing}})
    )

    assert release_version.main(["--series-check", tag]) == exit_code
    assert output.read_text() == github_output


@pytest.mark.parametrize(
    ("files", "publish"),
    [
        ([], True),
        ([{"yanked": True}], True),
        ([{"yanked": False}], False),
        ([{"yanked": True}, {"yanked": False}], False),
        ([{}], False),
    ],
)
def test_series_requires_available_files_but_reserves_every_version(tmp_path, monkeypatch, files, publish):
    version = "1.2.0.20260102"
    output = tmp_path / "github_output"
    monkeypatch.setenv("GITHUB_OUTPUT", str(output))
    monkeypatch.setattr(
        release_version, "urlopen",
        respond_with({"releases": {version: files, "1.1.0.20260102": [{"yanked": False}]}}),
    )

    assert release_version.series_check("v1.2.0", "1.2.0") == 0
    assert output.read_text() == f"publish={str(publish).lower()}\n"
    assert release_version.next_version("1.2.0", DAY, release_version.published_versions()) == version + ".1"


def test_sdk_version_flag_prints_the_sdk_version(capsys):
    assert release_version.main(["--sdk-version"]) == 0
    assert capsys.readouterr().out == release_version.read_sdk_version() + "\n"


def test_non_final_sdk_version_fails_with_a_message(monkeypatch, capsys):
    def non_final():
        raise ValueError("SDK version '1.3.0rc1' is not a final X.Y.Z release")

    monkeypatch.setattr(release_version, "read_sdk_version", non_final)
    assert release_version.main(["--series-check", "v1.3.0rc1"]) == 1
    assert "not a final X.Y.Z release" in capsys.readouterr().err
