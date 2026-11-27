import re
from pathlib import Path

from serpapi import __version__


def test_typing_extra_accepts_stubs_from_the_same_major():
    pyproject = (Path(__file__).resolve().parents[1] / "pyproject.toml").read_text()
    major = int(__version__.split(".")[0])
    assert re.findall(r"^typing = \[(.*)\]$", pyproject, re.MULTILINE) == [f'"serpapi-stubs>={major},<{major + 1}"']
