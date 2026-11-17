import html
import json

import pytest

import fetch_engines


def engine(*params):
    group = {"engine": {"type": "select"}}
    group.update({name: metadata for name, metadata in params})
    return {"serpapi_parameters": {"name": "SerpApi", "parameters": group}}


def playground(parameters):
    props = html.escape(json.dumps({"parameters": parameters}), quote=True)
    return f'<div data-react-props="{{&quot;other&quot;: 1}}"></div><div data-react-props="{props}"></div>'


@pytest.fixture
def few_engines(monkeypatch):
    monkeypatch.setattr(fetch_engines, "MIN_ENGINES", 2)


def test_extract_props_picks_element_with_parameters():
    assert fetch_engines.extract_props(playground({"google": {}})) == {"parameters": {"google": {}}}


def test_extract_props_requires_parameters():
    with pytest.raises(ValueError, match="no data-react-props"):
        fetch_engines.extract_props('<div data-react-props="{}"></div>')


@pytest.mark.parametrize(
    ("name", "metadata", "engine", "expected"),
    [
        ("name", {"type": "select", "options": [["active", "Active"], ["off", "Off"]]}, None, {"type": "select", "options": ["active", "off"]}),
        ("name", {"type": "dropdown", "options": ["a", "b"]}, None, {"type": "dropdown", "options": ["a", "b"]}),
        ("name", {"type": "device", "options": ["mobile", "tablet"]}, None, {"type": "device", "options": ["mobile", "tablet"]}),
        ("name", {"options": [["10", "10"], ["20", "20"]]}, None, {"value_type": "number"}),
        ("name", {"options": ["4.5", "-1.25"]}, None, {"value_type": "number"}),
        ("language", {"type": "select", "options": ["amazon.com|en_US", "amazon.co.uk|en_GB"]}, "amazon", {"type": "select", "options": ["en_US", "en_GB"]}),
        ("name", {"type": "select", "options": [[str(i) + "x", "x"] for i in range(fetch_engines.MAX_LITERAL_OPTIONS + 1)]}, None, {"type": "select", "value_type": "string"}),
        # The playground's `required` flags are often conditional, so the snapshot does not keep them.
        ("name", {"type": "checkbox", "required": True}, None, {"type": "checkbox"}),
        ("name", {"options": [[True, "yes"]]}, None, {}),
        # Options without a closed-choice type, such as a comma-separated multi-value list, are open strings.
        ("type_of_visit", {"options": ["Business", "Couples"], "html": "Separate values with a comma"}, None, {"value_type": "string"}),
        ("name", {"type": "text", "options": ["a", "b"]}, None, {"type": "text", "value_type": "string"}),
        # Values documented in a different case than the options mean matching is case-insensitive.
        ("mkt", {"type": "select", "options": ["en-us", "de-de"], "html": "Case insensitive, e.g. <code>en-US</code>"}, None, {"type": "select", "value_type": "string"}),
        ("cc", {"type": "select", "options": ["DE", "US"], "html": "<code>de</code> &mdash; <code>us</code>"}, None, {"type": "select", "value_type": "string"}),
        # Documented values that match exactly, or are unrelated to the options, keep the closed list.
        ("mkt", {"type": "select", "options": ["en-us", "de-de"], "html": "Use <code>en-us</code> or <code>de-de</code>"}, None, {"type": "select", "options": ["en-us", "de-de"]}),
        ("mkt", {"type": "select", "options": ["en-us", "de-de"], "html": "Defaults to <code>all</code>"}, None, {"type": "select", "options": ["en-us", "de-de"]}),
        # A listed value that the options lack means the option list cannot be trusted.
        ("sort_mode", {"type": "select", "options": ["relevance", "time"], "html": "<code>relevance</code> - by relevance<br><code>date</code> - by date."}, None, {"type": "select", "value_type": "string"}),
        ("tbm", {"type": "select", "options": ["isch", "vid"], "html": "<code>(no selection)</code> - regular search<br><code>isch</code> - images"}, None, {"type": "select", "options": ["isch", "vid"]}),
        ("sort_mode", {"type": "select", "options": ["relevance", "time"], "html": "<code>relevance</code>&nbsp;&mdash; by relevance<br><code>date</code> &ndash; by date."}, None, {"type": "select", "value_type": "string"}),
        # eBay's `_blrs` checkbox sends a value, not a flag.
        ("_blrs", {"type": "checkbox"}, "ebay", {"type": "checkbox", "value_type": "string"}),
    ],
)
def test_normalize_param(name, metadata, engine, expected):
    assert fetch_engines.normalize_param(name, metadata, engine) == expected


def test_normalize_props_sorts_and_excludes(few_engines):
    snapshot = fetch_engines.normalize_props(
        {
            "parameters": {
                "google": engine(("q", {}), ("device", {"type": "select", "options": [["mobile", "Mobile"]]})),
                "extract": engine(("url", {"required": True})),
                "google_light_fast": engine(),
            }
        }
    )
    assert list(snapshot["engines"]) == ["extract", "google"]
    assert list(snapshot["engines"]["google"]) == ["device", "engine", "q"]
    assert snapshot["engines"]["google"]["device"] == {"type": "select", "options": ["mobile"]}
    assert snapshot["engines"]["extract"]["url"] == {}


@pytest.mark.parametrize(
    ("parameters", "message"),
    [
        ({"google": engine(), "bing": {"group": {"parameters": {"q": {}}}}}, "no 'engine' parameter"),
        ({"google": engine(), "bing": engine()}, "missing expected engines: extract"),
        ({"google": engine(), "extract": {"group": []}}, "has no parameters object"),
    ],
)
def test_normalize_props_rejects_malformed_metadata(few_engines, parameters, message):
    with pytest.raises(ValueError, match=message):
        fetch_engines.normalize_props({"parameters": parameters})


def test_normalize_props_requires_minimum_engine_count():
    with pytest.raises(ValueError, match="expected at least"):
        fetch_engines.normalize_props({"parameters": {"google": engine(), "extract": engine()}})


def test_main_writes_snapshot_only_when_changed(tmp_path, few_engines, capsys):
    page = tmp_path / "playground.html"
    page.write_text(playground({"google": engine(("q", {})), "extract": engine()}), encoding="utf-8")
    output = tmp_path / "engines.json"

    assert fetch_engines.main(["--html", str(page), "--output", str(output)]) == 0
    assert json.loads(output.read_text())["engines"]["google"]["q"] == {}
    assert fetch_engines.main(["--html", str(page), "--output", str(output)]) == 0
    assert capsys.readouterr().out.splitlines()[-1].startswith("Unchanged")
