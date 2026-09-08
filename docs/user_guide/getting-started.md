---
title: "Getting Started"
description: "Install serpapi, create a client, and run your first search."
---

# Getting Started

The `serpapi` package lets you request search results from [SerpApi](https://serpapi.com) in Python. You need Python installed and a SerpApi account with an API key.

## Installation

Run one of these commands in your terminal. Use `pip` for an existing Python environment, `uv add` for a uv project, or `uv pip install` for a virtual environment managed with uv.

::::{tab-set}

:::{tab-item} pip

```bash
pip install serpapi
```

:::

:::{tab-item} uv project

```bash
uv add serpapi
```

:::

:::{tab-item} uv environment

```bash
uv pip install serpapi
```

:::

::::

The package requires Python 3.6 or newer.

Create or sign in to your SerpApi account and copy your API key from the [dashboard](https://serpapi.com/manage-api-key). An API key identifies your account when you make a request. Replace `secret_api_key` below with your key and run the command in your terminal. On Windows, use PowerShell.

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

## First Search

Save this code in a file named `search_example.py`. Run it with `python search_example.py` from the same terminal where you set the key. Use `python3` if that is the command for Python on your computer. If you installed the package with `uv add`, run `uv run python search_example.py` from your project directory.

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

`os.environ["SERPAPI_KEY"]` reads the key you set in the terminal. If Python raises `KeyError: 'SERPAPI_KEY'`, set the variable in the terminal where you run the script, or in your editor's run configuration.

`client.search()` sends the search to SerpApi. By default, the response uses JSON, a format for named fields and lists. The client converts it into a `SerpResults` object, which you can read like a Python dictionary. It also has methods such as `as_dict()`, `next_page()`, and `yield_pages()`.

`results["organic_results"]` is a list of unpaid search results. Python counts list positions from zero, so `[0]` selects the first result. The example prints its title and link. For searches that may return no results, use the loop shown in [Output Formats](output-formats.md#json).

## What the Parameters Mean

The example above sends a Google Search request:

| Parameter | Purpose |
| --- | --- |
| `engine` | Selects the SerpApi engine. `google` is Google Search. |
| `q` | Text to search for, such as `coffee shops`. |
| `location` | Location to search from, such as `Austin, Texas`. |
| `hl` | Language for the Google interface. `en` is English. |
| `gl` | Country for Google results. `us` is the United States. |

Each engine has its own search parameters, listed in the [SerpApi API documentation](https://serpapi.com/search-api). Use the [SerpApi Playground](https://serpapi.com/playground) to try a search in your browser and copy the parameters into Python.

## When to Use the Client

Create a `serpapi.Client` when you need to make several requests, fetch more pages, or run searches at the same time. You can reuse its API key, timeout, and HTTP session, which manages connections to SerpApi.

For a single search, you can also call `serpapi.search()` directly:

```python
import serpapi

results = serpapi.search(
    api_key="secret_api_key",
    engine="google",
    q="coffee",
)
```

To reuse the same settings for later searches, create a client:

```python
client = serpapi.Client(api_key="secret_api_key", timeout=20)
results = client.search(engine="google", q="coffee")
```

## Next Steps

- Read [Client Usage](client-usage.md) for response helpers, request options, and archive helpers.
- Read [Pagination](pagination.md) when collecting more than one page of results.
- Try [Google Across Countries](../examples/google-across-countries.md) to compare results from different countries.
