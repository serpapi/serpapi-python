#!/usr/bin/env python3
"""Build static typing stubs from SerpApi engine parameter metadata."""

from __future__ import annotations

import argparse
import ast
import filecmp
import json
import keyword
import re
import sys
import tempfile
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable

SCRIPT_DIR = Path(__file__).resolve().parent
REPO_ROOT = SCRIPT_DIR.parent
ENGINE_DIR = SCRIPT_DIR / "engines"
OUTPUT_DIR = REPO_ROOT / "serpapi"
GENERATED_FILES = ("__init__.pyi", "core.pyi", "engine_params.pyi", "py.typed")
MAX_LITERAL_OPTIONS = 80
REQUEST_KWARGS = ("timeout", "proxies", "verify", "stream", "cert")
CLIENT_OPTIONAL_COMMON_PARAMS = {"api_key"}
DIRECT_SEARCH_SPECIAL_PARAMS = {"engine", "output"}
BOOLEAN_PARAM_NAMES = {"async", "include_filters", "no_cache", "zero_trace"}


@dataclass(frozen=True)
class Param:
    name: str
    typ: str
    required: bool
    direct_keyword: bool


@dataclass(frozen=True)
class Engine:
    name: str
    class_name: str
    params: tuple[Param, ...]


def to_class_name(engine: str) -> str:
    parts = re.split(r"[^0-9A-Za-z]+", engine)
    return "".join(part[:1].upper() + part[1:] for part in parts if part) + "SearchParams"


def is_direct_keyword(name: str) -> bool:
    return name.isidentifier() and not keyword.iskeyword(name)


def unique_values(values: Iterable[Any]) -> list[Any]:
    seen = set()
    unique = []
    for value in values:
        key = (type(value).__name__, repr(value))
        if key in seen:
            continue
        seen.add(key)
        unique.append(value)
    return unique


def literal_type(values: list[Any]) -> str | None:
    values = unique_values(values)
    if not values or len(values) > MAX_LITERAL_OPTIONS:
        return None
    if not all(isinstance(value, (str, int, bool)) for value in values):
        return None
    return "Literal[" + ", ".join(type_literal_value(value) for value in values) + "]"


def type_literal_value(value: Any) -> str:
    if isinstance(value, str):
        return json.dumps(value)
    return repr(value)


def fallback_option_type(values: list[Any]) -> str:
    values = unique_values(values)
    if values and all(isinstance(value, str) for value in values):
        return "str"
    if values and all(isinstance(value, bool) for value in values):
        return "bool"
    if values and all(isinstance(value, (int, float)) for value in values):
        return "Union[float, int]"
    return "Any"


def param_type(name: str, metadata: dict[str, Any], engine: str) -> str:
    param_kind = metadata.get("type")
    options = metadata.get("options")

    if name == "engine":
        return f'Literal["{engine}"]'
    if name == "api_key":
        return "str"
    if name == "output":
        return 'Literal["json", "html"]'
    if name in BOOLEAN_PARAM_NAMES or param_kind == "checkbox":
        return "bool"
    if param_kind == "number":
        return "Union[float, int]"
    if isinstance(options, list):
        return literal_type(options) or fallback_option_type(options)
    if param_kind in {"device", "dropdown", "select"}:
        return "str"
    if param_kind == "location":
        return "str"
    return "str"


def load_engine_definitions(engine_dir: Path = ENGINE_DIR) -> list[Engine]:
    if not engine_dir.exists():
        raise FileNotFoundError(f"Engine metadata directory does not exist: {engine_dir}")

    engines = []
    for path in sorted(engine_dir.glob("*.json")):
        payload = json.loads(path.read_text(encoding="utf-8"))
        engine = payload.get("engine")
        if not isinstance(engine, str) or not engine:
            raise ValueError(f"{path} is missing a string 'engine' value")

        merged_params: dict[str, dict[str, Any]] = {}
        for section in ("common_params", "params"):
            params = payload.get(section, {})
            if not isinstance(params, dict):
                raise ValueError(f"{path} has invalid '{section}' metadata")
            for name, metadata in params.items():
                if not isinstance(name, str) or not name:
                    raise ValueError(f"{path} contains an invalid parameter name")
                if not isinstance(metadata, dict):
                    raise ValueError(f"{path} parameter {name!r} metadata is not an object")
                merged_params[name] = metadata

        params = []
        for name in sorted(merged_params):
            metadata = merged_params[name]
            required = bool(metadata.get("required")) and name not in CLIENT_OPTIONAL_COMMON_PARAMS
            params.append(
                Param(
                    name=name,
                    typ=param_type(name, metadata, engine),
                    required=required,
                    direct_keyword=is_direct_keyword(name),
                )
            )

        if not any(param.name == "engine" for param in params):
            params.append(
                Param(
                    name="engine",
                    typ=f'Literal["{engine}"]',
                    required=True,
                    direct_keyword=True,
                )
            )

        engines.append(Engine(name=engine, class_name=to_class_name(engine), params=tuple(params)))

    if not engines:
        raise ValueError(f"No engine metadata files found in {engine_dir}")
    return engines


def generated_header() -> str:
    return (
        "# This file is generated by typing/generate_type_stubs.py.\n"
        "# Do not edit by hand; update typing/engines/*.json and rerun the generator.\n\n"
    )


def output_param(typ: str, *, required: bool) -> Param:
    return Param("output", typ, required, True)


def search_params_variant_names(engine: Engine) -> tuple[str, str]:
    suffix = "SearchParams"
    prefix = engine.class_name[: -len(suffix)] if engine.class_name.endswith(suffix) else engine.class_name
    return f"{prefix}JsonSearchParams", f"{prefix}HtmlSearchParams"


def format_typed_dict(engine: Engine, *, class_name: str, output: Param | None = None) -> list[str]:
    lines = [
        f"{class_name} = TypedDict(",
        f'    "{class_name}",',
        "    {",
    ]
    has_output = False
    for param in engine.params:
        typed_param = output if param.name == "output" and output else param
        if typed_param.name == "output":
            has_output = True
        wrapper = "Required" if typed_param.required else "NotRequired"
        lines.append(f'        "{typed_param.name}": {wrapper}[{typed_param.typ}],')
    if output and not has_output:
        wrapper = "Required" if output.required else "NotRequired"
        lines.append(f'        "{output.name}": {wrapper}[{output.typ}],')
    lines.extend(
        [
            "    },",
            "    total=False,",
            ")",
            "",
        ]
    )
    return lines


def build_engine_params_stub(engines: list[Engine]) -> str:
    lines = [
        generated_header().rstrip(),
        "from typing import Any, Union",
        "from typing_extensions import Literal, NotRequired, Required, TypedDict",
        "",
    ]
    for engine in engines:
        json_params, html_params = search_params_variant_names(engine)
        lines.extend(
            format_typed_dict(
                engine,
                class_name=json_params,
                output=output_param('Literal["json"]', required=False),
            )
        )
        lines.extend(
            format_typed_dict(
                engine,
                class_name=html_params,
                output=output_param('Literal["html"]', required=True),
            )
        )
        lines.append(f"{engine.class_name} = Union[{json_params}, {html_params}]")
        lines.append("")
    union = ", ".join(engine.class_name for engine in engines)
    lines.append(f"SearchParams = Union[{union}]")
    lines.append("")
    return "\n".join(lines)


def direct_params(engine: Engine, *, html_output: bool, omit_engine: bool) -> list[Param]:
    skipped = {"output"}
    if omit_engine:
        skipped.add("engine")
    params = []
    for param in engine.params:
        if param.name in skipped or param.name in REQUEST_KWARGS:
            continue
        if not param.direct_keyword:
            continue
        if param.name == "engine" and not omit_engine:
            params.append(Param(param.name, f'Literal["{engine.name}"]', True, True))
        elif param.name == "api_key":
            params.append(Param(param.name, param.typ, False, True))
        else:
            params.append(param)

    if html_output:
        params.append(Param("output", 'Literal["html"]', True, True))
    else:
        params.append(Param("output", 'Literal["json"]', False, True))

    for name in REQUEST_KWARGS:
        params.append(Param(name, "Any", False, True))
    return sorted(params, key=lambda param: (not param.required, param.name))


def format_search_overload(
    *,
    receiver: str | None,
    params: list[Param],
    return_type: str,
) -> list[str]:
    lines = ["@overload", "def search("]
    if receiver:
        lines.append(f"    {receiver},")
    lines.append("    *,")
    for param in params:
        default = "" if param.required else " = ..."
        lines.append(f"    {param.name}: {param.typ}{default},")
    lines.append(f") -> {return_type}: ...")
    lines.append("")
    return lines


def format_params_dict_overload(
    *,
    receiver: str | None,
    params_type: str,
    return_type: str,
) -> list[str]:
    lines = ["@overload", "def search("]
    if receiver:
        lines.append(f"    {receiver},")
    lines.extend(
        [
            f"    params: {params_type},",
            "    *,",
        ]
    )
    for name in REQUEST_KWARGS:
        lines.append(f"    {name}: Any = ...,")
    lines.append(f") -> {return_type}: ...")
    lines.append("")
    return lines


def format_params_dict_overloads(*, receiver: str | None, engine: Engine) -> list[str]:
    json_params, html_params = search_params_variant_names(engine)
    lines = []
    lines.extend(
        format_params_dict_overload(
            receiver=receiver,
            params_type=html_params,
            return_type="str",
        )
    )
    lines.extend(
        format_params_dict_overload(
            receiver=receiver,
            params_type=json_params,
            return_type="SerpResults",
        )
    )
    lines.append("")
    return lines


def format_search_overloads(engines: list[Engine], *, receiver: str | None) -> list[str]:
    lines = []
    for engine in engines:
        lines.extend(format_params_dict_overloads(receiver=receiver, engine=engine))
        lines.extend(
            format_search_overload(
                receiver=receiver,
                params=direct_params(engine, html_output=True, omit_engine=False),
                return_type="str",
            )
        )
        lines.extend(
            format_search_overload(
                receiver=receiver,
                params=direct_params(engine, html_output=False, omit_engine=False),
                return_type="SerpResults",
            )
        )
        if engine.name == "google":
            lines.extend(
                format_search_overload(
                    receiver=receiver,
                    params=direct_params(engine, html_output=True, omit_engine=True),
                    return_type="str",
                )
            )
            lines.extend(
                format_search_overload(
                    receiver=receiver,
                    params=direct_params(engine, html_output=False, omit_engine=True),
                    return_type="SerpResults",
                )
            )
    lines.extend(
        [
            "@overload",
            "def search(",
        ]
    )
    if receiver:
        lines.append(f"    {receiver},")
    lines.extend(
        [
            "    params: Mapping[str, Any],",
            "    *,",
        ]
    )
    for name in REQUEST_KWARGS:
        lines.append(f"    {name}: Any = ...,")
    lines.append(") -> Union[SerpResults, str]: ...")
    lines.append("")
    return lines


def build_core_stub(engines: list[Engine]) -> str:
    lines = [
        generated_header().rstrip(),
        "from typing import Any, Dict, List, Mapping, Optional, Union, overload",
        "",
        "from .engine_params import (",
    ]
    for engine in engines:
        json_params, html_params = search_params_variant_names(engine)
        lines.append(f"    {json_params},")
        lines.append(f"    {html_params},")
    lines.extend(
        [
            ")",
            "from .http import HTTPClient",
            "from .models import SerpResults",
            "from typing_extensions import Literal",
            "",
            "",
            "class Client(HTTPClient):",
            "    DASHBOARD_URL: str",
            "",
            "    def __init__(self, *, api_key: Optional[str] = ..., timeout: Any = ...) -> None: ...",
            "    def __repr__(self) -> str: ...",
            "",
        ]
    )
    for line in format_search_overloads(engines, receiver="self"):
        lines.append("    " + line if line else "")
    lines.extend(
        [
            "    def search_archive(self, params: Optional[Mapping[str, Any]] = ..., **kwargs: Any) -> Union[SerpResults, str]: ...",
            "    def locations(self, params: Optional[Mapping[str, Any]] = ..., **kwargs: Any) -> List[Dict[str, Any]]: ...",
            "    def account(self, params: Optional[Mapping[str, Any]] = ..., **kwargs: Any) -> Dict[str, Any]: ...",
            "",
        ]
    )
    lines.extend(format_search_overloads(engines, receiver=None))
    lines.extend(
        [
            "def search_archive(params: Optional[Mapping[str, Any]] = ..., **kwargs: Any) -> Union[SerpResults, str]: ...",
            "def locations(params: Optional[Mapping[str, Any]] = ..., **kwargs: Any) -> List[Dict[str, Any]]: ...",
            "def account(params: Optional[Mapping[str, Any]] = ..., **kwargs: Any) -> Dict[str, Any]: ...",
            "",
        ]
    )
    return "\n".join(lines)


def build_init_stub() -> str:
    return "\n".join(
        [
            generated_header().rstrip(),
            "from .__version__ import __version__ as __version__",
            "from .core import Client as Client, account as account, locations as locations, search as search, search_archive as search_archive",
            "from .exceptions import APIKeyNotProvided as APIKeyNotProvided, HTTPConnectionError as HTTPConnectionError, HTTPError as HTTPError, SearchIDNotProvided as SearchIDNotProvided, SerpApiError as SerpApiError, TimeoutError as TimeoutError",
            "from .models import SerpResults as SerpResults",
            "",
        ]
    )


def validate_stub_syntax(path: Path, content: str) -> None:
    if path.suffix == ".pyi":
        ast.parse(content, filename=str(path))


def write_if_changed(path: Path, content: str) -> bool:
    validate_stub_syntax(path, content)
    if path.exists() and path.read_text(encoding="utf-8") == content:
        return False

    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")
    return True


def generate_stubs(engine_dir: Path = ENGINE_DIR, output_dir: Path = OUTPUT_DIR) -> list[Path]:
    engines = load_engine_definitions(engine_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    outputs = {
        "__init__.pyi": build_init_stub(),
        "core.pyi": build_core_stub(engines),
        "engine_params.pyi": build_engine_params_stub(engines),
        "py.typed": "",
    }
    written = []
    for name in GENERATED_FILES:
        path = output_dir / name
        if write_if_changed(path, outputs[name]):
            written.append(path)
    return written


def check_generated(engine_dir: Path, output_dir: Path) -> bool:
    with tempfile.TemporaryDirectory() as tmp_dir:
        expected_dir = Path(tmp_dir) / "serpapi"
        generate_stubs(engine_dir, expected_dir)

        ok = True
        for name in GENERATED_FILES:
            expected = expected_dir / name
            actual = output_dir / name
            if not actual.exists():
                print(f"Missing generated typing file: {actual}", file=sys.stderr)
                ok = False
                continue
            if not filecmp.cmp(expected, actual, shallow=False):
                print(f"Generated typing file is stale: {actual}", file=sys.stderr)
                ok = False
        return ok


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--engine-dir", type=Path, default=ENGINE_DIR)
    parser.add_argument("--output-dir", type=Path, default=OUTPUT_DIR)
    parser.add_argument("--check", action="store_true", help="verify generated files are current")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(sys.argv[1:] if argv is None else argv)
    if args.check:
        if check_generated(args.engine_dir, args.output_dir):
            print("Generated typing stubs are up to date.")
            return 0
        return 1

    written = generate_stubs(args.engine_dir, args.output_dir)
    print(f"Wrote {len(written)} typing files to {args.output_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
