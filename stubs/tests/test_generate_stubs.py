import ast
import json

import pytest

import generate_stubs

SNAPSHOT = {
    "engines": {
        "google": {
            "engine": {},
            "q": {"required": True},
            "device": {"type": "select", "options": ["desktop", "mobile"]},
            "num": {"type": "number"},
            "nfpr": {"type": "checkbox"},
            "async": {},
        },
        "google_lens": {"engine": {"required": True}, "url": {"required": True}, "image_id": {}},
        "google_translate": {"engine": {"required": True}, "from": {"required": True}, "text": {}},
        "naver": {"engine": {"required": True}, "page": {}, "start": {}, "num": {}},
        "extract": {"engine": {"required": True}, "url": {"required": True}, "timeout": {"type": "number"}},
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
    assert google["device"].typ == 'Literal["desktop", "mobile"]'
    assert google["num"].typ == "_Number"
    assert google["nfpr"].typ == "_Flag"
    assert google["async"].typ == "_Flag"
    assert google["q"].typ == "_Scalar"
    naver = params(engines["naver"])
    assert naver["page"].typ == "_Number"
    assert naver["start"].typ == "_Number"
    assert naver["num"].typ == "_Number"


@pytest.mark.parametrize(
    ("name", "metadata", "expected"),
    [
        # The SDK sends numbers as text, so a parameter the playground leaves untyped accepts them.
        ("min_price", {}, "_Scalar"),
        ("store_id", {"required": True}, "_Scalar"),
        ("mkt", {"type": "select", "value_type": "string"}, "str"),
        ("location", {"type": "location"}, "str"),
        ("type_of_visit", {"value_type": "string"}, "str"),
        ("api_key", {}, "str"),
    ],
)
def test_untyped_params_accept_numbers(name, metadata, expected):
    assert generate_stubs.param_type(name, metadata) == expected


def test_only_api_mandatory_params_are_required(engines):
    assert not params(engines["google"])["q"].required
    assert not params(engines["google_lens"])["url"].required
    assert params(engines["extract"])["url"].required


def test_only_google_can_omit_engine(tmp_path):
    path = tmp_path / "engines.json"
    # The playground's `required` flag on `engine` must not decide this.
    path.write_text(
        json.dumps(
            {
                "engines": {
                    "google": {"engine": {"required": True}, "q": {}},
                    "bing": {"engine": {}, "q": {}},
                    "extract": {"engine": {}, "url": {"required": True}},
                }
            }
        )
    )
    loaded = {engine.name: engine for engine in generate_stubs.load_engines(path)}
    assert not loaded["google"].engine_required
    assert loaded["bing"].engine_required


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
    assert '"from": NotRequired[_Scalar]' in outputs["engine_params.pyi"]
    assert '"url": Required[_Scalar]' in outputs["engine_params.pyi"]
    assert "params: None = None" in core


def test_only_extract_accepts_read_only_mappings(snapshot):
    core = generate_stubs.render(snapshot)["core.pyi"]

    def fallback(function):
        overloads = core.split(f"def {function}(")[1:]
        return next(overload.split(") ->")[0] for overload in overloads if "**kwargs: Any," in overload.split(") ->")[0])

    assert "params: Union[SearchParams, MutableMapping[str, Any]]," in fallback("search")
    assert "params: Union[SearchArchiveParams, MutableMapping[str, Any]]," in fallback("search_archive")
    assert "params: Mapping[str, Any]," in fallback("extract")
    assert "def locations(params: Optional[MutableMapping[str, Any]] = None" in core


def test_google_can_omit_engine(snapshot):
    core = generate_stubs.render(snapshot)["core.pyi"]
    search_overloads = core.split("def search(")[1:]
    assert any("engine:" not in overload.split(") ->")[0] and "q: _Scalar" in overload for overload in search_overloads)


def test_check_reports_stale_files(snapshot, tmp_path, capsys):
    out = tmp_path / "out"
    assert generate_stubs.main(["--snapshot", str(snapshot), "--output-dir", str(out), "--check"]) == 1
    assert generate_stubs.main(["--snapshot", str(snapshot), "--output-dir", str(out)]) == 0
    assert generate_stubs.main(["--snapshot", str(snapshot), "--output-dir", str(out), "--check"]) == 0
    assert "out of date" in capsys.readouterr().err


def test_committed_stubs_match_snapshot():
    assert generate_stubs.stale_files(generate_stubs.render()) == []
