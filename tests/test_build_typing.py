import importlib.util
import os
import sys
from pathlib import Path

import pytest


def load_build_typing_module():
    module_path = Path(__file__).resolve().parents[1] / "typing" / "generate_type_stubs.py"
    spec = importlib.util.spec_from_file_location("generate_type_stubs", module_path)
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def test_write_if_changed_validates_stub_content_before_replacing_existing_file(tmp_path):
    build_typing = load_build_typing_module()
    target = tmp_path / "serpapi" / "generated.pyi"
    original = "value: int\n"
    target.parent.mkdir()
    target.write_text(original, encoding="utf-8")

    with pytest.raises(SyntaxError):
        build_typing.write_if_changed(target, "def broken(: ...\n")

    assert target.read_text(encoding="utf-8") == original


def test_write_if_changed_skips_unchanged_content(tmp_path):
    build_typing = load_build_typing_module()
    target = tmp_path / "serpapi" / "generated.pyi"
    content = "value: int\n"
    target.parent.mkdir()
    target.write_text(content, encoding="utf-8")
    os.utime(target, (1_700_000_000, 1_700_000_000))
    original_mtime = target.stat().st_mtime_ns

    changed = build_typing.write_if_changed(target, content)

    assert changed is False
    assert target.read_text(encoding="utf-8") == content
    assert target.stat().st_mtime_ns == original_mtime


def test_generator_defaults_to_typing_engine_metadata():
    build_typing = load_build_typing_module()
    repo_root = Path(__file__).resolve().parents[1]

    assert build_typing.ENGINE_DIR == repo_root / "typing" / "engines"
    assert build_typing.OUTPUT_DIR == repo_root / "serpapi"


def test_generated_header_points_to_typing_sources():
    build_typing = load_build_typing_module()

    header = build_typing.generated_header()

    assert "typing/generate_type_stubs.py" in header
    assert "typing/engines/*.json" in header


def test_engine_params_stub_splits_json_and_html_search_params():
    build_typing = load_build_typing_module()
    engine = build_typing.Engine(
        name="example",
        class_name="ExampleSearchParams",
        params=(
            build_typing.Param("engine", 'Literal["example"]', True, True),
            build_typing.Param("output", 'Literal["json", "html"]', False, True),
            build_typing.Param("q", "str", True, True),
        ),
    )

    stub = build_typing.build_engine_params_stub([engine])

    assert "ExampleJsonSearchParams = TypedDict(" in stub
    assert '        "output": NotRequired[Literal["json"]],' in stub
    assert "ExampleHtmlSearchParams = TypedDict(" in stub
    assert '        "output": Required[Literal["html"]],' in stub
    assert "ExampleSearchParams = Union[ExampleJsonSearchParams, ExampleHtmlSearchParams]" in stub


def test_dict_search_overloads_narrow_return_type_by_output():
    build_typing = load_build_typing_module()
    engine = build_typing.Engine(
        name="example",
        class_name="ExampleSearchParams",
        params=(
            build_typing.Param("engine", 'Literal["example"]', True, True),
            build_typing.Param("output", 'Literal["json", "html"]', False, True),
            build_typing.Param("q", "str", True, True),
        ),
    )

    stub = build_typing.build_core_stub([engine])

    assert "params: ExampleHtmlSearchParams" in stub
    assert "params: ExampleJsonSearchParams" in stub
    assert "params: Mapping[str, Any]" in stub
    assert ") -> str: ..." in stub
    assert ") -> SerpResults: ..." in stub
    assert ") -> Union[SerpResults, str]: ..." in stub
