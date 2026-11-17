# serpapi-stubs

Type stubs for [`serpapi`](https://pypi.org/project/serpapi/), the official SerpApi Python client. They describe the parameters of every SerpApi engine, so mypy, pyright, and IDEs can autocomplete parameter names and flag typos or invalid option values before a request is sent.

The stubs are typing-only. They do not change runtime behavior.

## Installation

Install them through the SDK's `typing` extra:

```sh
pip install "serpapi[typing]"
```

The extra installs the newest stubs built for the installed SDK version.

SDK 1.2.0 was released before the extra existed, so pip ignores `[typing]` there and warns that the extra does not exist. Install its stubs directly:

```sh
pip install "serpapi-stubs==1.2.0.*"
```

Stubs are not published for SDK versions older than 1.2.0.

## Usage

Keyword arguments are checked against the selected engine:

```python
import serpapi

client = serpapi.Client(api_key="...")
client.search(engine="google", q="coffee", device="mobile")  # OK
client.search(engine="google", q="coffee", locaton="Austin")  # error: unexpected keyword "locaton"
client.search(engine="google", q="coffee", device="watch")  # error: invalid option
html = client.search(engine="bing", q="coffee", output="html")  # str, not SerpResults
```

A plain dict is accepted as before. Its keys are checked only when you annotate it with a parameter type from `serpapi.engine_params`. That module exists only for type checkers, so import it under `TYPE_CHECKING`:

```python
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from serpapi.engine_params import GoogleJsonSearchParams

params: "GoogleJsonSearchParams" = {"engine": "google", "q": "coffee"}
results = client.search(params)
```

Each engine has `<Engine>JsonSearchParams`, `<Engine>TextSearchParams` (for `output="html"` or `"md"`), and their union `<Engine>SearchParams`. `SearchParams` covers every engine. Extract and the Search Archive use `ExtractParams` and `SearchArchiveParams`.

Notes:

- `async` and `from` are Python keywords, so pass them in the params dict: `client.search({"engine": "google", "q": "coffee", "async": True})`.
- In keyword calls, `timeout` is the HTTP request timeout. Pass Extract's API `timeout` parameter in the params dict.
- Keyword calls need literal `engine` and `output` values so the checker can select the engine's overload. A `str` variable, or `**` unpacking of a `Dict[str, str]`, is rejected. When either value is computed at runtime, pass a params dict, or type the value as `Literal` or `Final`.
- A `dict` variable that is not annotated with a parameter type gives a `SerpResults | Any` result, because the checker cannot see its `output` value. Pass `output="md"` or `output="html"` as a keyword to get `str`, or `output="json"` to get `SerpResults`. The keyword overrides any `output` in the mapping.
- `search()`, `search_archive()`, `locations()`, and `account()` write the API key into the mapping they receive, so pass a `dict` or a `serpapi.engine_params` type. A read-only `Mapping` or your own `TypedDict` is rejected; pass `dict(params)` instead. `extract()` copies its mapping and accepts any `Mapping`.
- Pyright reports `reportMissingModuleSource` for `serpapi.engine_params` because the module has no runtime source. Importing it under `TYPE_CHECKING` is safe.

Engine parameters come from the [SerpApi Playground](https://serpapi.com/playground). Parameters that SerpApi has not documented there are reported as errors. Use a `# type: ignore` comment or an untyped `dict` if you need one. Parameters that the Playground gives no type accept `str`, `int`, or `float`, because the SDK sends numbers as text.

The Playground sometimes uses UI-specific values rather than the API values (for example, Amazon language choices combine a domain and locale). The stubs normalize those choices to the API's documented locale codes. A parameter is typed as a closed set of options only when the Playground presents it as a single-choice list that agrees with its documentation. Parameters that document case-insensitive values (such as Bing's `mkt`, `cc`, and `safeSearch`), comma-separated values (such as Tripadvisor Reviews' `type_of_visit`), or a value missing from the list (such as Yandex's `sort_mode`) are typed `str`. When an engine parameter is not present in the Playground, pass a mapping to `search()`; mapping calls remain compatible with runtime-supported parameters without weakening keyword checks.

## Versions

Stub versions use the SDK version they describe, followed by the release date: `1.2.0.20260715` contains stubs for `serpapi` 1.2.0 published on 2026-07-15. A second release on the same day adds a counter, such as `1.2.0.20260715.1`.

Stub releases currently support final numeric SDK versions only (`X.Y.Z`). Prerelease, post-release, and development SDK versions are not supported by the stub versioning scheme or its exact-series extra pin.

`serpapi[typing]` requires `serpapi-stubs==<SDK version>.*`, so you get stub updates for your SDK version only. New stubs are published with each SDK release and whenever parameter metadata changes between SDK releases.

A stub update can add, remove, or narrow parameters as SerpApi engines change. That can make code that passed type checking fail it, but runtime behavior never changes. To control when you take these updates, pin the stubs alongside the extra or use a lockfile:

```sh
pip install "serpapi[typing]" "serpapi-stubs==1.2.0.20260715"
```

A stub release that breaks valid code is yanked from PyPI and fixed in a newer release.

## Development

The stubs are built from the [`stubs/`](https://github.com/serpapi/serpapi-python/tree/master/stubs) directory of the SDK repository:

- `data/engines.json`: engine metadata collected from the SerpApi Playground.
- `serpapi-stubs/core.pyi` and `serpapi-stubs/engine_params.pyi`: generated from the snapshot. Do not edit them by hand.
- `serpapi-stubs/*.pyi`: the other stubs, maintained by hand.
- `tools/`: the fetcher, the generator, and the release version script.

Run these commands from the `stubs/` directory:

```sh
python tools/fetch_engines.py          # refresh data/engines.json
python tools/generate_stubs.py         # regenerate the generated stubs
python tools/generate_stubs.py --check # fail if the generated stubs are stale
python -m pytest                       # test the tooling
```

A scheduled workflow refreshes the snapshot every week and opens a pull request when it changes. CI also compares the stubs with the runtime SDK using `mypy.stubtest` and type-checks the samples in `tests/typecheck` with mypy and pyright. See the [contributing guide](https://github.com/serpapi/serpapi-python/blob/master/CONTRIBUTING.md#type-stubs) for the release process.
