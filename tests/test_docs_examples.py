import os

import pytest

from tests.docs_example_support import ROOT, docs_pages, python_blocks, run_page


PAGES = docs_pages()


@pytest.mark.parametrize("path", PAGES, ids=lambda path: path.relative_to(ROOT).as_posix())
def test_documentation_python_blocks_compile(path):
    for number, block in enumerate(python_blocks(path), start=1):
        compile(block["code"], f"{path}::python-block-{number}", "exec")


@pytest.mark.parametrize("path", PAGES, ids=lambda path: path.relative_to(ROOT).as_posix())
def test_documentation_examples_live(path, tmp_path):
    api_key = os.environ.get("SERPAPI_KEY") or os.environ.get("API_KEY")
    if not api_key:
        pytest.skip("Set SERPAPI_KEY or API_KEY to run live documentation examples")

    try:
        run_page(path, tmp_path, api_key)
    except RuntimeError as exc:
        pytest.fail(str(exc), pytrace=False)
