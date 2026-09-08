import json
import os
from pathlib import Path
import re
import shutil
import signal
import subprocess
import sys
import threading
from urllib.parse import parse_qs, urlsplit

import serpapi
from serpapi.http import HTTPClient


ROOT = Path(__file__).resolve().parents[1]
PYTHON_BLOCK_RE = re.compile(
    r"(?P<skip><!--\s*docs-test:\s*skip\b(?P<reason>.*?)-->\s*)?"
    r"```python\r?\n(?P<code>.*?)```",
    re.DOTALL,
)
PAGE_TIMEOUT = 300


def python_blocks(path):
    return [match.groupdict() for match in PYTHON_BLOCK_RE.finditer(path.read_text())]


def docs_pages():
    paths = [ROOT / "README.md", *sorted((ROOT / "docs").rglob("*.md"))]
    return [path for path in paths if "_build" not in path.parts and python_blocks(path)]


def redact(text, api_key=None):
    for key in (api_key, os.environ.get("SERPAPI_KEY"), os.environ.get("API_KEY")):
        if key:
            text = text.replace(key, "[REDACTED]")
    return text


def validate_response(response, path, params):
    if not 200 <= response.status_code < 300:
        raise AssertionError(f"HTTP {response.status_code}")

    content_type = response.headers.get("Content-Type", "").lower()
    if "json" in content_type:
        payload = response.json()
        if not isinstance(payload, (dict, list)) or not payload:
            raise AssertionError("Expected a nonempty JSON object or list")
        if isinstance(payload, dict):
            if payload.get("error"):
                raise AssertionError(str(payload["error"]))
            if payload.get("search_metadata", {}).get("status") == "Error":
                raise AssertionError("Search metadata reports an error")
            if path == "/image" and not payload.get("image_id"):
                raise AssertionError("Image upload did not return image_id")

    if path == "/search" or path.startswith("/searches/"):
        result = serpapi.SerpResults.from_http_response(response)
        output = params.get("output", "json")
        if output in ("md", "html"):
            if not isinstance(result, str) or not result.strip():
                raise AssertionError(f"output={output} did not return a nonempty string")
        elif not isinstance(result, serpapi.SerpResults):
            raise AssertionError("JSON search did not return SerpResults")


def install_http_checks():
    original_request = HTTPClient.request
    report_path = Path(os.environ["DOCS_EXAMPLE_REPORT_DIR"]) / f"{os.getpid()}.jsonl"
    lock = threading.Lock()

    def checked_request(self, method, path, params, **kwargs):
        url = urlsplit(path)
        query = {key: values[-1] for key, values in parse_qs(url.query).items()}
        query.update(params)
        record = {"path": url.path, "engine": query.get("engine"), "ok": False}
        if not self.timeout and not kwargs.get("timeout"):
            kwargs["timeout"] = 30
        try:
            response = original_request(self, method, path, params, **kwargs)
            validate_response(response, url.path, query)
            record["ok"] = True
            return response
        except Exception as exc:
            record["error"] = redact(f"{type(exc).__name__}: {exc}")
            raise
        finally:
            with lock, report_path.open("a") as report:
                report.write(json.dumps(record) + "\n")

    HTTPClient.request = checked_request


def script_for_page(path):
    parts = [
        "import os\nimport serpapi\n"
        "from tests.docs_example_support import install_http_checks\n"
        "install_http_checks()\n"
        'client = serpapi.Client(api_key=os.environ["SERPAPI_KEY"], timeout=30)\n'
    ]
    for number, block in enumerate(python_blocks(path), start=1):
        if block["skip"]:
            if not block["reason"].strip():
                raise RuntimeError(f"Python block {number} needs a docs-test skip reason")
            continue
        code = block["code"]
        for placeholder in ('"secret_api_key"', "'secret_api_key'"):
            code = code.replace(placeholder, 'os.environ["SERPAPI_KEY"]')
        parts.append(f"# Python block {number}\n{code}")
    return "\n\n".join(parts)


def run_page(path, workdir, api_key, timeout=PAGE_TIMEOUT):
    workdir.mkdir(parents=True, exist_ok=True)
    report_dir = workdir / "requests"
    report_dir.mkdir()
    script = workdir / "example.py"
    script.write_text(script_for_page(path))
    shutil.copyfile(ROOT / "assets" / "serpapi-icon.png", workdir / "image.png")
    env = os.environ.copy()
    env.update({
        "SERPAPI_KEY": api_key,
        "API_KEY": api_key,
        "DOCS_EXAMPLE_REPORT_DIR": str(report_dir),
        "PYTHONPATH": os.pathsep.join([str(ROOT / "tests"), str(ROOT)]),
    })
    with subprocess.Popen(
        [sys.executable, str(script)],
        cwd=workdir,
        env=env,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.PIPE,
        text=True,
        start_new_session=os.name == "posix",
    ) as process:
        try:
            _, stderr = process.communicate(timeout=timeout)
        except subprocess.TimeoutExpired:
            if os.name == "posix":
                os.killpg(process.pid, signal.SIGKILL)
            else:
                process.kill()
            process.communicate()
            raise RuntimeError(f"Example exceeded the {timeout}-second page limit") from None

    records = [
        json.loads(line)
        for report in sorted(report_dir.glob("*.jsonl"))
        for line in report.read_text().splitlines()
    ]
    errors = [record for record in records if not record["ok"]]
    if process.returncode or errors:
        details = "\n".join(
            f"{record['engine'] or record['path']}: {record['error']}"
            for record in errors
        )
        raise RuntimeError(redact(f"{details}\n{stderr}", api_key).strip())
    if not records:
        raise RuntimeError("Example finished without making a SerpApi request")
    return records
