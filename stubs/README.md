# serpapi-stubs

Type stubs for [`serpapi`](https://pypi.org/project/serpapi/), the official SerpApi Python client. They describe the parameters of every SerpApi engine, so mypy, pyright, and IDEs can autocomplete parameter names and flag typos or invalid option values before a request is sent.

The stub files are used by type checkers and IDEs, not by the running SDK.

## Installation

SDK 1.3.0 includes `AsyncClient` but predates the `typing` extra. Install the stubs alongside that SDK:

```sh
pip install "serpapi==1.3.0" "serpapi-stubs>=1,<2"
```

For async support on Python 3.11+, add the SDK's `async` extra:

```sh
pip install "serpapi[async]==1.3.0" "serpapi-stubs>=1,<2"
```

Starting with the SDK release that includes the `typing` extra, use `pip install "serpapi[typing]"` or `pip install "serpapi[async,typing]"`. A fresh install selects the newest compatible stubs; a plain SDK install does not request them.

Requests 2.34 and later includes its own types. On Python 3.10+ with Requests pinned below 2.34, install a compatible `types-requests` separately. On older Python versions the stubs install it automatically.

## Usage

Keyword arguments are checked against the selected engine:

```python
import serpapi

client = serpapi.Client(api_key="...")
client.search(engine="google", q="coffee", device="mobile")  # OK
client.search(engine="google", q="coffee", locaton="Austin")  # typo: use location
client.search(engine="google", q="coffee", device="watch")  # not a Google device option
html = client.search(engine="bing", q="coffee", output="html")  # str, not SerpResults
```

`AsyncClient` accepts the same engine parameters. Await the call for its result; iterate over pages with `async for`:

```python
async def search_pages():
    async with serpapi.AsyncClient(api_key="...") as client:
        results = await client.search(engine="google", q="coffee")  # AsyncSerpResults
        async for page in results.yield_pages(max_pages=2):
            if isinstance(page, str):
                print(page)
                break
            print(page.as_dict())
        html = await client.search(engine="bing", q="coffee", output="html")  # str
```

A plain dict is accepted as before. Annotate it with a parameter type from `serpapi.engine_params` to check its keys and get field-specific errors instead of mypy's list of candidate overloads. That module exists only for type checkers, so import it under `TYPE_CHECKING`:

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
- Set an optional query field to `None` to omit it or suppress a session default. Google `tbs` also accepts a sequence of strings, sent as repeated query parameters.
- `output="json_with_pixel_position"` ([Pixel Position](https://serpapi.com/pixel-position-api)) is accepted for `google`, `google_ads`, and the Search Archive. It returns `SerpResults` synchronously and `AsyncSerpResults` when awaited.
- For sync calls, `proxies` must be mutable because Requests updates it when merging environment proxies. Async calls copy the mapping, so a read-only mapping works too. A `None` value disables that configured proxy.
- Both clients raise `serpapi.HTTPError`. Use `exc.status_code` and `exc.error` for transport-independent details. The inherited request and response annotations describe Requests, but async errors can carry httpx2 objects. For transport-specific attributes, pass `exc.response` or `exc.request` to a helper whose parameter is typed `object`, then narrow it with `isinstance(response, httpx2.Response)` or `isinstance(request, httpx2.Request)`.
- Keyword calls need literal `engine` and `output` values so the checker can select the engine's overload. A `str` variable, or `**` unpacking of a `Dict[str, str]`, is rejected. When either value is computed at runtime, pass a params dict, or type the value as `Literal` or `Final`.
- A `dict` variable that is not annotated with a parameter type gives a `SerpResults | Any` result, because the checker cannot see its `output` value. Pass `output="md"` or `output="html"` as a keyword to get `str`, or `output="json"` to get `SerpResults`. The keyword overrides any `output` in the mapping.
- Sync `search()` and `search_archive()` (including their module-level helpers) write overrides back into the original dictionary. To request JSON with a text-typed dictionary, use `client.search(dict(params), output="json")`; reusing `params` still requests text. With a typed dictionary, pass other overrides by name (`start=10`) or unpack a `TypedDict` with known keys. If the override keys are only known at runtime, pass `dict(params)` so an `output` override cannot change the original. Sync `extract()` and the async methods already copy their input.
- `next_page()` can return raw text instead of a result object, and returns `None` when there is no next page. If `yield_pages()` yields a string, handle it and break: text has no next-page link. This applies to sync and async pagination.
- On the sync client, `search()`, `search_archive()`, `locations()`, and `account()` write the API key into the mapping they receive, so pass a `dict` or a `serpapi.engine_params` type. A read-only `Mapping` or your own `TypedDict` is rejected; pass `dict(params)` instead. Sync `extract()` and all async methods that take search parameters copy the mapping and accept any `Mapping`.
- Pyright reports `reportMissingModuleSource` for `serpapi.engine_params` because the module has no runtime source. Importing it under `TYPE_CHECKING` is safe.

Engine parameters come from the [SerpApi Playground](https://serpapi.com/playground). Parameters that SerpApi has not documented there are reported as errors. Use a `# type: ignore` comment or an untyped `dict` if you need one. Parameters that the Playground gives no type accept `str`, `int`, or `float`, because the SDK sends numbers as text.

The Playground sometimes uses UI-specific values rather than the API values (for example, Amazon language choices combine a domain and locale). The stubs normalize those choices to the API's documented locale codes. A parameter is typed as a closed set of options only when the Playground presents it as a single-choice list that agrees with its documentation. Parameters that document case-insensitive values (such as `mkt`, `cc`, and `safeSearch` for `bing` and `bing_news`), comma-separated values (such as Tripadvisor Reviews' `type_of_visit`), or a value missing from the list (such as Yandex's `sort_mode` and Walmart's `sort`) are typed `str`. These checks apply per engine: `bing_images` documents only lowercase `safeSearch` choices, so its type remains `Literal["strict", "moderate", "off"]`. When an engine parameter is not present in the Playground, pass a mapping to `search()`; mapping calls remain compatible with runtime-supported parameters without weakening keyword checks.

## Versions

Stub versions start with the SDK version used to build them, followed by the UTC release date, for example `1.3.0.YYYYMMDD`. The prefix identifies the build, not the oldest compatible SDK. A second release that day adds `.1`; later releases increment the highest published suffix for that SDK and date rather than filling gaps.

Stub releases can only be built from final numeric SDK versions (`X.Y.Z`).

The 1.x SDK's `typing` extra requests `serpapi-stubs>=1,<2`. Each stub wheel declares the SDK versions it supports (currently `serpapi>=1.3.0,<2`). New engine parameters can reach older SDKs without a runtime upgrade. If a later stub wheel needs a new client method, its minimum SDK goes up: a fresh install with the older SDK pinned selects the newest wheel that still supports it.

A stub update can add, remove, or narrow parameters as SerpApi engines change. Code that previously passed type checking can then fail the check even if the SDK hasn't changed.

Installing or upgrading `serpapi-stubs` on its own can also upgrade `serpapi` to satisfy the wheel's requirements. To keep the SDK fixed while refreshing stubs, pin it in the same command, for example `pip install --upgrade "serpapi==1.3.0" "serpapi-stubs>=1,<2"`, or supply an SDK pin in a constraints file. To freeze both versions, use a lockfile.

Before yanking a broken stub release, maintainers make sure every affected supported SDK still has an installable alternative.

## Development

Building this distribution from source requires Python 3.9 or newer for `setuptools>=77`. Installing a published wheel does not require the build backend. Use Python 3.13 for development checks, matching CI.

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
