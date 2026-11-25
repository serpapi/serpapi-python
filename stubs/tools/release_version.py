#!/usr/bin/env python3
"""Compute and write the next serpapi-stubs version: <SDK version>.<UTC YYYYMMDD>[.<n>]."""

from __future__ import annotations

import argparse
import datetime
import json
import os
import re
import sys
from pathlib import Path
from typing import Iterable
from urllib.error import HTTPError
from urllib.request import Request, urlopen

STUBS_ROOT = Path(__file__).resolve().parent.parent
SDK_VERSION_FILE = STUBS_ROOT.parent / "serpapi" / "__version__.py"
VERSION_FILE = STUBS_ROOT / "VERSION"
PYPI_JSON_URL = "https://pypi.org/pypi/serpapi-stubs/json"
SDK_PYPI_JSON_URL = "https://pypi.org/pypi/serpapi/json"
FINAL_RELEASE = re.compile(r"[0-9]+\.[0-9]+\.[0-9]+")


def read_sdk_version(path: Path = SDK_VERSION_FILE) -> str:
    match = re.search(r"""^__version__\s*=\s*["']([^"']+)["']""", path.read_text(encoding="utf-8"), re.MULTILINE)
    if not match:
        raise ValueError(f"Could not find __version__ in {path}")
    version = match.group(1)
    if not FINAL_RELEASE.fullmatch(version):
        raise ValueError(
            f"SDK version {version!r} is not a final X.Y.Z release such as 1.2.0; "
            "serpapi-stubs versions append a date segment and only follow final SDK releases."
        )
    return version


def next_version(sdk_version: str, date: datetime.date, existing: Iterable[str]) -> str:
    published = set(existing)
    base = f"{sdk_version}.{date:%Y%m%d}"
    if base not in published:
        return base
    serial = 1
    while f"{base}.{serial}" in published:
        serial += 1
    return f"{base}.{serial}"


def has_published_series(sdk_version: str, existing: Iterable[str]) -> bool:
    prefix = f"{sdk_version}."
    return any(version.startswith(prefix) for version in existing)


def published_versions(url: str = PYPI_JSON_URL, *, available_only: bool = False) -> set[str]:
    request = Request(url, headers={"Accept": "application/json"})
    try:
        with urlopen(request, timeout=30) as response:
            payload = json.load(response)
    except HTTPError as error:
        if error.code == 404:
            return set()
        raise
    releases = payload["releases"]
    if available_only:
        return {
            version for version, files in releases.items()
            if any(not file.get("yanked", False) for file in files)
        }
    return set(releases)


def parse_date(value: str) -> datetime.date:
    return datetime.datetime.strptime(value, "%Y%m%d").date()


def series_check(tag: str, sdk_version: str) -> int:
    """For an SDK release tag: verify it names the SDK version and report whether its stubs still need publishing."""
    if tag != f"v{sdk_version}":
        print(f"Release tag {tag!r} does not match SDK version tag 'v{sdk_version}'", file=sys.stderr)
        return 1
    # Preserve an installable series, but allow recovery when all its files were yanked or deleted.
    publish = not has_published_series(sdk_version, published_versions(available_only=True))
    print(f"{'Publishing' if publish else 'Skipping'} stubs for SDK {sdk_version}")
    github_output = os.environ.get("GITHUB_OUTPUT")
    if github_output:
        with open(github_output, "a", encoding="utf-8") as handle:
            handle.write(f"publish={'true' if publish else 'false'}\n")
    return 0


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--date", type=parse_date, help="release date as YYYYMMDD (default: today in UTC)")
    parser.add_argument("--offline", action="store_true", help="do not query PyPI for existing versions")
    parser.add_argument("--output", type=Path, default=VERSION_FILE, help="file that setuptools reads the version from")
    parser.add_argument("--sdk-version", action="store_true", help="print the SDK version and exit")
    parser.add_argument("--sdk-published", action="store_true", help="print whether this exact SDK version is installable from PyPI")
    parser.add_argument(
        "--series-check",
        metavar="TAG",
        help="check an SDK release tag and write publish=true/false to GITHUB_OUTPUT instead of a version",
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(sys.argv[1:] if argv is None else argv)
    try:
        sdk_version = read_sdk_version()
    except ValueError as error:
        print(error, file=sys.stderr)
        return 1
    if args.sdk_version:
        print(sdk_version)
        return 0
    if args.sdk_published:
        print("true" if sdk_version in published_versions(SDK_PYPI_JSON_URL, available_only=True) else "false")
        return 0
    if args.series_check is not None:
        return series_check(args.series_check, sdk_version)
    date = args.date or datetime.datetime.now(datetime.timezone.utc).date()
    existing = set() if args.offline else published_versions()
    version = next_version(sdk_version, date, existing)
    args.output.write_text(version + "\n", encoding="utf-8")
    print(version)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
