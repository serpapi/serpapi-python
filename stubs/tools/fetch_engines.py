#!/usr/bin/env python3
"""Fetch SerpApi engine parameters from the playground and write a normalized snapshot."""

from __future__ import annotations

import argparse
import html
import json
import math
import os
import re
import sys
import tempfile
from html.parser import HTMLParser
from pathlib import Path
from typing import Any
from urllib.request import Request, urlopen

PLAYGROUND_URL = "https://serpapi.com/playground"
SNAPSHOT_PATH = Path(__file__).resolve().parent.parent / "data" / "engines.json"
EXCLUDED_ENGINES = frozenset({"google_scholar_profiles", "google_light_fast", "google_lens_image_sources"})
REQUIRED_ENGINES = ("google", "extract")
MIN_ENGINES = 50
MAX_LITERAL_OPTIONS = 80
# Playground parameter types whose options are the complete list of accepted values.
CLOSED_CHOICE_TYPES = frozenset({"select", "dropdown", "device"})
DOCUMENTED_VALUE = re.compile(r"<code>(.*?)</code>", re.DOTALL)
# A value in a documented list of choices: `<code>value</code> - label`.
LISTED_VALUE = re.compile(r"<code>([\w.\-]+)</code>\s+[-–—]\s")
# A parenthesised list of example values: `(e.g. <code>a</code>, <code>b</code>)`.
EXAMPLE_LIST = re.compile(r"\(e\.g\.([^)]*)\)", re.IGNORECASE)
# A value in such a list. `for <code>...</code>` says what an example applies to and is not a value:
# `<code>USD</code> for <code>airbnb.com</code>`.
EXAMPLE_VALUE = re.compile(r"(?<!for )<code>(.*?)</code>", re.DOTALL)
# Checkboxes that send a value instead of a flag: eBay's `_blrs` takes `spell_auto_correct`.
VALUE_CHECKBOXES = frozenset({("ebay", "_blrs")})
TIMEOUT_SECONDS = 60
USER_AGENT = "serpapi-stubs-refresh (+https://github.com/serpapi/serpapi-python)"


class _ReactPropsParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.props: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        for name, value in attrs:
            if name == "data-react-props" and value:
                self.props.append(value)


def extract_props(page_html: str) -> dict[str, Any]:
    parser = _ReactPropsParser()
    parser.feed(page_html)
    for raw in parser.props:
        props = json.loads(raw)
        if isinstance(props, dict) and isinstance(props.get("parameters"), dict):
            return props
    raise ValueError("Playground HTML has no data-react-props element with engine parameters")


def _option_value(option: Any) -> Any:
    return option[0] if isinstance(option, list) and option else option


def _is_numeric(value: Any) -> bool:
    if isinstance(value, bool):
        return False
    if isinstance(value, int):
        return True
    if isinstance(value, float):
        return math.isfinite(value)
    if isinstance(value, str):
        try:
            return math.isfinite(float(value))
        except ValueError:
            return False
    return False


def _is_closed_choice(metadata: dict[str, Any], values: list[str]) -> bool:
    """Whether the options are the only accepted values, so a Literal type does not reject valid calls."""
    if metadata.get("type") not in CLOSED_CHOICE_TYPES:
        return False
    description = metadata.get("html")
    if not isinstance(description, str):
        return True
    # Decode entities first, so that `&mdash;` separators and escaped values compare as displayed.
    description = html.unescape(description)
    accepted = set(values)
    folded = {value.casefold() for value in values}
    # Some options are documented in another case than the option list (e.g. Bing's `mkt`, `cc`), which
    # means the API does not match case-sensitively.
    for token in DOCUMENTED_VALUE.findall(description):
        value = token.strip()
        if value not in accepted and value.casefold() in folded:
            return False
    # A listed value that the options lack means the option list is wrong or incomplete (Yandex's
    # `sort_mode` offers `time` where the API takes `date`).
    if not all(value.casefold() in folded for value in LISTED_VALUE.findall(description)):
        return False
    # So does an example list that mixes options with other values (Walmart's `sort` documents `new`).
    # Examples that name no option at all usually belong to another parameter.
    for examples in EXAMPLE_LIST.findall(description):
        known = [token.strip().casefold() in folded for token in EXAMPLE_VALUE.findall(examples)]
        if any(known) and not all(known):
            return False
    return True


def normalize_param(name: str, metadata: Any, engine: str | None = None) -> dict[str, Any]:
    if not isinstance(metadata, dict):
        raise ValueError(f"Parameter {name!r} metadata is not an object")
    param: dict[str, Any] = {}
    param_type = metadata.get("type")
    if isinstance(param_type, str) and param_type:
        param["type"] = param_type
    if (engine, name) in VALUE_CHECKBOXES:
        param["value_type"] = "string"
    options = metadata.get("options")
    if isinstance(options, list) and options:
        values = []
        for option in options:
            value = _option_value(option)
            if isinstance(value, (str, int, float)) and not isinstance(value, bool) and value not in values:
                values.append(value)
        if name == "language" and engine and engine.startswith("amazon"):
            values = list(dict.fromkeys(value.rsplit("|", 1)[-1] for value in values if isinstance(value, str)))
        if values and any(_is_numeric(value) for value in values):
            param["value_type"] = "number"
        elif values:
            literal = len(values) <= MAX_LITERAL_OPTIONS and all(isinstance(value, str) for value in values)
            if literal and _is_closed_choice(metadata, values):
                param["options"] = values
            else:
                param["value_type"] = "string"
    return param


def normalize_props(props: dict[str, Any]) -> dict[str, Any]:
    parameters = props.get("parameters")
    if not isinstance(parameters, dict):
        raise ValueError("Playground props are missing the 'parameters' object")

    engines: dict[str, dict[str, Any]] = {}
    for engine, groups in parameters.items():
        if not isinstance(engine, str) or not engine or engine in EXCLUDED_ENGINES:
            continue
        if not isinstance(groups, dict):
            raise ValueError(f"Engine {engine!r} metadata is not an object")
        params: dict[str, Any] = {}
        for group_name, group in groups.items():
            group_params = group.get("parameters") if isinstance(group, dict) else None
            if not isinstance(group_params, dict):
                raise ValueError(f"Engine {engine!r} group {group_name!r} has no parameters object")
            for name, metadata in group_params.items():
                if not isinstance(name, str) or not name:
                    raise ValueError(f"Engine {engine!r} has an invalid parameter name")
                params[name] = normalize_param(name, metadata, engine)
        if "engine" not in params:
            raise ValueError(f"Engine {engine!r} has no 'engine' parameter")
        engines[engine] = {name: params[name] for name in sorted(params)}

    missing = [engine for engine in REQUIRED_ENGINES if engine not in engines]
    if missing:
        raise ValueError(f"Playground metadata is missing expected engines: {', '.join(missing)}")
    if len(engines) < MIN_ENGINES:
        raise ValueError(f"Playground metadata has only {len(engines)} engines; expected at least {MIN_ENGINES}")

    return {"source": PLAYGROUND_URL, "engines": {name: engines[name] for name in sorted(engines)}}


def render_snapshot(snapshot: dict[str, Any]) -> str:
    return json.dumps(snapshot, indent=2, ensure_ascii=False) + "\n"


def write_atomic(path: Path, content: str) -> bool:
    if path.exists() and path.read_text(encoding="utf-8") == content:
        return False
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp_name = tempfile.mkstemp(dir=path.parent, prefix=f".{path.name}.", suffix=".tmp")
    try:
        with os.fdopen(fd, "w", encoding="utf-8", newline="\n") as handle:
            handle.write(content)
        os.replace(tmp_name, path)
    except BaseException:
        Path(tmp_name).unlink(missing_ok=True)
        raise
    return True


def download_playground(url: str = PLAYGROUND_URL) -> str:
    request = Request(url, headers={"User-Agent": USER_AGENT})
    with urlopen(request, timeout=TIMEOUT_SECONDS) as response:
        return response.read().decode("utf-8")


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--html", type=Path, help="read a saved playground page instead of downloading it")
    parser.add_argument("--output", type=Path, default=SNAPSHOT_PATH)
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(sys.argv[1:] if argv is None else argv)
    page_html = args.html.read_text(encoding="utf-8") if args.html else download_playground()
    snapshot = normalize_props(extract_props(page_html))
    changed = write_atomic(args.output, render_snapshot(snapshot))
    state = "Updated" if changed else "Unchanged"
    print(f"{state} {args.output} ({len(snapshot['engines'])} engines)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
