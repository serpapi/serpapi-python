---
title: "Getting Started"
description: "Install serpapi, create a client, and run your first search."
guide-section: "Basics"
---

# Getting Started

SerpApi Python is the official Python client for [SerpApi](https://serpapi.com). It wraps SerpApi HTTP endpoints with a small Python API while keeping request parameters close to the underlying API.

Use this page to install the package, configure your API key, and make a first Google Search request.

## Installation

:::{.panel-tabset}

## pip

```bash
pip install serpapi
```

## uv project

```bash
uv add serpapi
```

## uv environment

```bash
uv pip install serpapi
```

:::

Python 3.6 or newer is required by the package.

Create or sign in to your SerpApi account, copy your API key from the [dashboard](https://serpapi.com/manage-api-key), and set it in the environment:

:::{.panel-tabset}

## macOS / Linux

```bash
export SERPAPI_KEY="secret_api_key"
```

## Windows

```powershell
$env:SERPAPI_KEY = "secret_api_key"
```

:::

## First Search

```python
import os
import serpapi

client = serpapi.Client(api_key=os.environ["SERPAPI_KEY"], timeout=20)

results = client.search(
    engine="google",
    q="coffee shops",
    location="Austin, Texas",
    hl="en",
    gl="us",
)

first_result = results["organic_results"][0]
print(first_result["title"])
print(first_result["link"])
```

`client.search()` returns a `SerpResults` object for JSON responses. It behaves like a dictionary and adds helpers such as `as_dict()`, `next_page()`, and `yield_pages()`.

## What the Parameters Mean

The example above sends a Google Search request:

| Parameter | Purpose |
| --- | --- |
| `engine` | Selects the SerpApi engine. `google` is Google Search. |
| `q` | Search query. |
| `location` | Search location used by SerpApi. |
| `hl` | Interface language. |
| `gl` | Country for Google results. |

SerpApi supports many engines and engine-specific parameters. The authoritative list lives in the [SerpApi API documentation](https://serpapi.com/search-api). The [SerpApi Playground](https://serpapi.com/playground) is the fastest way to build and test a request before moving it into Python.

## When to Use the Client

Use `serpapi.Client` for application code, scripts that make more than one request, pagination, and concurrent workloads. The client stores the API key, timeout, and HTTP session configuration in one place.

The module-level helpers are useful for quick experiments:

```python
import serpapi

results = serpapi.search(
    api_key="secret_api_key",
    engine="google",
    q="coffee",
)
```

For production code, prefer a client instance:

```python
client = serpapi.Client(api_key="secret_api_key", timeout=20)
results = client.search(engine="google", q="coffee")
```

## Next Steps

- Read [Client Usage](client-usage.md) for response helpers, request options, and archive helpers.
- Read [Pagination](pagination.md) when collecting more than one page of results.
- Try [Google Across Countries](../docs/examples/google-across-countries.md) for a practical localization example.
