import os
import subprocess
import sys
from textwrap import dedent

import pytest
import requests

from tests.docs_example_support import ROOT, run_page, validate_response


MOCK_REQUEST = """
import json
import requests

def fake_request(self, **kwargs):
    response = requests.Response()
    response.status_code = 200
    response.headers['Content-Type'] = 'application/json'
    response._content = json.dumps({'organic_results': [{'title': 'Coffee'}]}).encode()
    return response

requests.Session.request = fake_request
"""


def markdown_page(tmp_path, code):
    path = tmp_path / "page.md"
    path.write_text("```python\n" + dedent(code) + "\n```\n")
    return path


def test_doc_runner_executes_main_guard_and_spawned_workers(tmp_path):
    code = MOCK_REQUEST + """
from concurrent.futures import ProcessPoolExecutor
import multiprocessing

def search_worker(query):
    results = client.search(q=query)
    return results['organic_results'][0]['title']

if __name__ == '__main__':
    with ProcessPoolExecutor(max_workers=2, mp_context=multiprocessing.get_context('spawn')) as pool:
        assert list(pool.map(search_worker, ['one', 'two'])) == ['Coffee', 'Coffee']
"""
    page = markdown_page(tmp_path, code)
    records = run_page(page, tmp_path / "run", "test-key")
    assert len(records) == 2
    assert all(record["ok"] for record in records)


def test_doc_runner_preserves_block_state_and_skips_marked_examples(tmp_path):
    page = markdown_page(tmp_path, MOCK_REQUEST + "\nquery = 'coffee'\n")
    with page.open("a") as source:
        source.write("""
<!-- docs-test: skip requires a user-supplied proxy -->
```python
raise RuntimeError('This block must not run')
```
```python
from pathlib import Path
assert Path('image.png').read_bytes().startswith(b'\\x89PNG')
client = serpapi.Client(api_key='secret_api_key')
assert client.api_key == os.environ['SERPAPI_KEY']
results = client.search(q=query)
assert results['organic_results'][0]['title'] == 'Coffee'
```
""")
    assert len(run_page(page, tmp_path / "run", "test-key")) == 1
    assert "test-key" not in (tmp_path / "run" / "example.py").read_text()


def test_doc_runner_fails_on_caught_api_errors_and_redacts_key(tmp_path):
    code = MOCK_REQUEST.replace(
        "{'organic_results': [{'title': 'Coffee'}]}",
        "{'error': os.environ['SERPAPI_KEY']}",
    ) + """
try:
    client.search(q='coffee')
except AssertionError:
    pass
"""
    page = markdown_page(tmp_path, code)
    with pytest.raises(RuntimeError) as failure:
        run_page(page, tmp_path / "run", "private-test-key")
    assert "[REDACTED]" in str(failure.value)
    assert "private-test-key" not in str(failure.value)
    for report in (tmp_path / "run" / "requests").glob("*.jsonl"):
        assert "private-test-key" not in report.read_text()


def test_doc_runner_rejects_examples_without_requests(tmp_path):
    page = markdown_page(tmp_path, "if __name__ == 'docs_examples':\n    client.search(q='coffee')")
    with pytest.raises(RuntimeError, match="without making a SerpApi request"):
        run_page(page, tmp_path / "run", "test-key")


def test_doc_runner_stops_a_stalled_example(tmp_path):
    page = markdown_page(tmp_path, "import time\ntime.sleep(60)")
    with pytest.raises(RuntimeError, match="page limit"):
        run_page(page, tmp_path / "run", "test-key", timeout=1)


@pytest.mark.parametrize("output", ["md", "html"])
def test_doc_response_check_rejects_json_for_text_output(output):
    response = requests.Response()
    response.status_code = 200
    response.headers["Content-Type"] = "application/json"
    response._content = b'{"organic_results": [{"title": "Coffee"}]}'
    with pytest.raises(AssertionError, match="nonempty string"):
        validate_response(response, "/search", {"output": output})


def test_doc_gate_fails_without_a_key():
    env = os.environ.copy()
    env.pop("SERPAPI_KEY", None)
    env.pop("API_KEY", None)
    result = subprocess.run(
        [sys.executable, "-m", "pytest", "tests/test_docs_examples.py",
         "--require-docs-key", "--collect-only", "-q"],
        cwd=ROOT, env=env, capture_output=True, text=True,
    )
    assert result.returncode != 0
    assert "Live docs checks require SERPAPI_KEY or API_KEY" in result.stderr
