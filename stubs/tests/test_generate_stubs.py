import ast
import json
import re
from pathlib import Path

import pytest

import generate_stubs

SNAPSHOT = {
    "engines": {
        "google": {
            "engine": {},
            "q": {},
            "device": {"type": "select", "options": ["desktop", "mobile"]},
            "num": {"type": "number"},
            "nfpr": {"type": "checkbox"},
            "async": {},
        },
        "google_lens": {"engine": {}, "url": {}, "image_id": {}},
        "google_translate": {"engine": {}, "from": {}, "text": {}},
        "naver": {"engine": {}, "page": {}, "start": {}, "num": {}},
        "extract": {"engine": {}, "url": {}, "timeout": {"type": "number"}},
    }
}


@pytest.fixture
def snapshot(tmp_path):
    path = tmp_path / "engines.json"
    path.write_text(json.dumps(SNAPSHOT))
    return path


@pytest.fixture
def engines(snapshot):
    return {engine.name: engine for engine in generate_stubs.load_engines(snapshot)}


def params(engine):
    return {param.name: param for param in engine.params}


def test_param_types(engines):
    google = params(engines["google"])
    assert google["device"].typ == 'Optional[Literal["desktop", "mobile"]]'
    assert google["num"].typ == "Optional[_Number]"
    assert google["nfpr"].typ == "Optional[_Flag]"
    assert google["async"].typ == "Optional[_Flag]"
    assert google["q"].typ == "Optional[_Scalar]"
    naver = params(engines["naver"])
    assert naver["page"].typ == "Optional[_Number]"
    assert naver["start"].typ == "Optional[_Number]"
    assert naver["num"].typ == "Optional[_Number]"


@pytest.mark.parametrize(
    ("name", "metadata", "expected"),
    [
        # The SDK sends numbers as text, so a parameter the playground leaves untyped accepts them.
        ("min_price", {}, "_Scalar"),
        ("mkt", {"type": "select", "value_type": "string"}, "str"),
        ("location", {"type": "location"}, "str"),
        ("type_of_visit", {"value_type": "string"}, "str"),
        ("api_key", {}, "str"),
    ],
)
def test_only_untyped_params_accept_numbers(name, metadata, expected):
    assert generate_stubs.param_type(name, metadata) == expected


def test_checkbox_that_sends_a_value_is_not_a_flag():
    assert generate_stubs.param_type("_blrs", {"type": "checkbox", "value_type": "string"}) == "str"


def test_request_options_match_the_sdk():
    # Keyword calls only accept the request options listed here, so a new SDK option must be added too.
    core = (Path(__file__).resolve().parents[2] / "serpapi" / "core.py").read_text(encoding="utf-8")
    sdk_options = {frozenset(re.findall(r'"(\w+)"', keys)) for keys in re.findall(r"for key in \[(.*?)\]", core)}
    assert sdk_options == {generate_stubs.REQUEST_OPTION_NAMES}


def test_only_api_mandatory_params_are_required(engines):
    assert not params(engines["google"])["q"].required
    assert not params(engines["google_lens"])["url"].required
    assert params(engines["extract"])["url"].required


def test_engine_is_required_except_for_google(engines):
    assert not engines["google"].engine_required
    assert all(engine.engine_required for name, engine in engines.items() if name != "google")


def test_keyword_overloads_skip_names_python_cannot_pass(engines):
    names = {param.name for param in generate_stubs.keyword_params(list(engines["google"].params), text=False)}
    assert "async" not in names
    assert {"q", "device", "output", "timeout"} <= names

    translate = {param.name for param in generate_stubs.keyword_params(list(engines["google_translate"].params), text=False)}
    assert "from" not in translate and "text" in translate


def test_extract_timeout_keyword_is_the_http_timeout(engines):
    timeouts = [param for param in generate_stubs.keyword_params(list(engines["extract"].params), text=False) if param.name == "timeout"]
    assert [param.typ for param in timeouts] == ["_Timeout"]


def test_rendered_stubs_are_valid_and_cover_engine_shapes(snapshot):
    outputs = generate_stubs.render(snapshot)
    for content in outputs.values():
        ast.parse(content)
    core = outputs["core.pyi"]
    assert "engine: Literal[\"google\"]" in core
    assert '"from": NotRequired[Optional[_Scalar]]' in outputs["engine_params.pyi"]
    assert '"url": Required[_Scalar]' in outputs["engine_params.pyi"]
    assert "params: None = None" in core


def fallbacks(core, function, definition="def"):
    """The (signature, return type) of each untyped mapping fallback, in order."""
    found = []
    for overload in core.split(f"    {definition} {function}(")[1:]:
        signature, _, rest = overload.partition(") -> ")
        if "params: Mapping[" in signature or "params: MutableMapping[" in signature:
            found.append((signature, rest.split(":")[0]))
    return found


def test_only_extract_accepts_read_only_mappings(snapshot):
    core = generate_stubs.render(snapshot)["core.pyi"]
    assert "params: MutableMapping[str, Any]," in fallbacks(core, "search")[-1][0]
    assert "params: MutableMapping[str, Any]," in fallbacks(core, "search_archive")[-1][0]
    assert "params: Mapping[str, Any]," in fallbacks(core, "extract")[-1][0]
    assert "def locations(params: Optional[MutableMapping[str, Any]] = None" in core


@pytest.mark.parametrize(
    ("function", "json_values"),
    [
        ("search", 'Literal["json", "json_with_pixel_position"]'),
        ("extract", 'Literal["json"]'),
        ("search_archive", 'Literal["json", "json_with_pixel_position"]'),
    ],
)
@pytest.mark.parametrize(("definition", "result"), [("def", "SerpResults"), ("async def", "AsyncSerpResults")])
def test_output_keyword_decides_the_fallback_return_type(snapshot, function, json_values, definition, result):
    # Both literal-output overloads must precede the catch-all.
    text, json_output, catch_all = fallbacks(generate_stubs.render(snapshot)["core.pyi"], function, definition)
    assert 'output: Literal["html", "md"],' in text[0] and text[1] == "str"
    assert f"output: {json_values}," in json_output[0] and json_output[1] == result
    assert "output:" not in catch_all[0] and catch_all[1] == f"Union[{result}, Any]"


def test_pixel_position_output_is_limited_to_the_apis_that_document_it(snapshot):
    outputs = generate_stubs.render(snapshot)
    pixel = 'Literal["json", "json_with_pixel_position"]'

    def typed_dict(name):
        return outputs["engine_params.pyi"].split(f"{name} = TypedDict(")[1].split("\n)\n")[0]

    assert f'"output": NotRequired[{pixel}]' in typed_dict("GoogleJsonSearchParams")
    assert f'"output": NotRequired[{pixel}]' in typed_dict("SearchArchiveJsonParams")
    assert '"output": NotRequired[Literal["json"]]' in typed_dict("NaverJsonSearchParams")
    assert '"output": NotRequired[Literal["json"]]' in typed_dict("ExtractJsonParams")
    # A keyword call selects the same values as the engine's TypedDict.
    keyword_calls = [call.split(") ->")[0] for call in outputs["core.pyi"].split("def search(")[1:] if "params: None" in call]
    assert any('engine: Literal["google"]' in call and f"output: {pixel} = ..." in call for call in keyword_calls)
    assert not any('engine: Literal["naver"]' in call and "json_with_pixel_position" in call for call in keyword_calls)


def test_google_can_omit_engine(snapshot):
    core = generate_stubs.render(snapshot)["core.pyi"]
    search_overloads = core.split("def search(")[1:]
    assert any("engine:" not in overload.split(") ->")[0] and "q: Optional[_Scalar]" in overload for overload in search_overloads)


def test_check_reports_stale_files(snapshot, tmp_path, capsys):
    out = tmp_path / "out"
    assert generate_stubs.main(["--snapshot", str(snapshot), "--output-dir", str(out), "--check"]) == 1
    assert generate_stubs.main(["--snapshot", str(snapshot), "--output-dir", str(out)]) == 0
    assert generate_stubs.main(["--snapshot", str(snapshot), "--output-dir", str(out), "--check"]) == 0
    assert "out of date" in capsys.readouterr().err


def test_committed_stubs_match_snapshot():
    assert generate_stubs.stale_files(generate_stubs.render()) == []
