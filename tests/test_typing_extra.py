import re
from pathlib import Path

from serpapi import __version__


def test_typing_extra_pins_stubs_to_sdk_release_series():
    pyproject = (Path(__file__).resolve().parents[1] / "pyproject.toml").read_text()
    assert re.findall(r"^typing = \[(.*)\]$", pyproject, re.MULTILINE) == [f'"serpapi-stubs=={__version__}.*"']
