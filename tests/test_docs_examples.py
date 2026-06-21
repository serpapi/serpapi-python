import os
import re
from pathlib import Path

import pytest
import serpapi


ROOT = Path(__file__).resolve().parents[1]
PYTHON_BLOCK_RE = re.compile(
    r"(?P<skip><!--\s*docs-test:\s*skip\b.*?-->\s*)?```python\n(?P<code>.*?)```",
    re.DOTALL,
)
API_KEY = os.environ.get("SERPAPI_KEY") or os.environ.get("API_KEY")


def docs_pages():
    return [
        ROOT / "README.md",
        ROOT / "docs" / "index.md",
        *sorted((ROOT / "docs" / "user_guide").glob("*.md")),
        *sorted((ROOT / "docs" / "examples").glob("*.md")),
    ]


def runnable_block(block):
    if API_KEY is None:
        return block

    return (
        block
        .replace('"secret_api_key"', repr(API_KEY))
        .replace("'secret_api_key'", repr(API_KEY))
    )


@pytest.mark.skipif(API_KEY is None, reason="SERPAPI_KEY or API_KEY is required")
@pytest.mark.parametrize("path", docs_pages(), ids=lambda path: path.relative_to(ROOT).as_posix())
def test_markdown_python_blocks_execute(path, monkeypatch):
    monkeypatch.setenv("SERPAPI_KEY", API_KEY)
    monkeypatch.setenv("API_KEY", API_KEY)

    blocks = list(PYTHON_BLOCK_RE.finditer(path.read_text(encoding="utf-8")))
    assert blocks, f"{path} has no Python examples"

    namespace = {
        "__name__": "docs_examples",
        "client": serpapi.Client(api_key=API_KEY, timeout=20),
        "os": os,
        "serpapi": serpapi,
    }
    for number, block in enumerate(blocks, start=1):
        if block.group("skip"):
            continue

        code = runnable_block(block.group("code"))
        exec(compile(code, f"{path}::python-block-{number}", "exec"), namespace)
