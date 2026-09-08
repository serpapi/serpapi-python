---
title: "SerpApi Python Library & Package"
description: "Search Google and other engines from Python with the official SerpApi client."
---

# SerpApi Python Library & Package

`serpapi` is the official Python client for [SerpApi](https://serpapi.com). Use it to search the web and read the results in your Python programs.

SerpApi supports Google, Google Maps, Google Shopping, Bing, DuckDuckGo, Baidu, Yandex, Yahoo, eBay, YouTube, App Stores, Walmart, Home Depot, Naver, and many more engines.

You can retrieve web search results, local business listings, shopping results, flight schedules, stock market data, job listings, trends, news headlines, AI Overview answers, and video search results.

## Install

Run one of these commands in your terminal. Use `pip` to install into your Python environment, or `uv add` if you manage your project with uv.

::::{tab-set}

:::{tab-item} pip

```bash
pip install serpapi
```

:::

:::{tab-item} uv

```bash
uv add serpapi
```

:::

::::

The package requires Python 3.6 or newer.

## First Request

Sign up at [SerpApi](https://serpapi.com/users/sign_up) and copy your API key from the [dashboard](https://serpapi.com/manage-api-key). Replace `secret_api_key` below with your key, then run the command in your terminal. On Windows, use PowerShell.

::::{tab-set}

:::{tab-item} macOS / Linux

```bash
export SERPAPI_KEY="secret_api_key"
```

:::

:::{tab-item} Windows

```powershell
$env:SERPAPI_KEY = "secret_api_key"
```

:::

::::

Run this code in a Python script or interpreter started from the same terminal so it can read `SERPAPI_KEY`:

```python
import os
import serpapi

client = serpapi.Client(api_key=os.environ["SERPAPI_KEY"])
results = client.search(
    engine="google",
    q="coffee",
    location="Austin, Texas",
    hl="en",
    gl="us",
)

print(results["organic_results"][0]["link"])
```

This prints the link from the first organic result, which is an unpaid search listing. `results["organic_results"]` is a list, and `[0]` selects its first item. See [Getting Started](user_guide/getting-started.md) for setup instructions and an explanation of each parameter.

The `results` variable contains a `SerpResults` object. You can read its fields like a Python dictionary, convert it to a plain dictionary, or use its methods to fetch more pages. You can also retrieve saved searches with `client.search_archive()`.

Use the same search parameter names as the [SerpApi API documentation](https://serpapi.com/search-api). The [SerpApi Playground](https://serpapi.com/playground) lets you try a search in your browser and copy its parameters into Python.

## Documentation Map

- [Getting Started](user_guide/getting-started.md) covers installation and your first search. [Client Usage](user_guide/client-usage.md) explains how to make requests and read responses.
- [AI Agents](ai-agents.md) covers search tools, Markdown results, and API references for agents.
- [Output Formats](user_guide/output-formats.md) explains when to use JSON, Markdown, or HTML.
- [Migration Guide](user_guide/migrating-from-google-search-results.md) shows how to replace `google-search-results` with this package.
- [Parameters and Engines](user_guide/parameters-and-engines.md) explains search parameters and how to test them in the [SerpApi Playground](https://serpapi.com/playground).
- For scripts that collect results, see [pagination](user_guide/pagination.md), [timeouts and errors](user_guide/errors-and-timeouts.md), [request options](user_guide/request-options.md), and [account and locations](user_guide/account-and-locations.md).
- For searches you retrieve later, selected response fields, and data retention settings, see [Async Search Archive](user_guide/async-search-archive.md), [JSON Restrictor](user_guide/json-restrictor.md), and [Zero Trace](user_guide/zero-trace.md).
- [Examples](examples/index.md) includes searches for web pages, AI answers, local businesses, products, travel, finance, trends, jobs, media, apps, and research.

```{toctree}
:hidden:
:maxdepth: 2
:caption: Basics

user_guide/getting-started
user_guide/client-usage
```

```{toctree}
:hidden:
:maxdepth: 2
:caption: User Guide

User Guide Overview <user_guide/index>
user_guide/parameters-and-engines
user_guide/output-formats
user_guide/pagination
user_guide/errors-and-timeouts
user_guide/account-and-locations
```

```{toctree}
:hidden:
:maxdepth: 2
:caption: Migration

user_guide/migrating-from-google-search-results
```

```{toctree}
:hidden:
:maxdepth: 2
:caption: Advanced Usage

user_guide/async-search-archive
user_guide/threading
user_guide/multiprocessing
user_guide/zero-trace
user_guide/json-restrictor
user_guide/request-options
```

```{toctree}
:hidden:
:maxdepth: 2
:caption: AI Agents

ai-agents
```

```{toctree}
:hidden:
:maxdepth: 3

examples/index
```

```{toctree}
:hidden:
:maxdepth: 2
:caption: Reference

reference
```
