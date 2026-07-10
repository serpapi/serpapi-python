---
title: "SerpApi Python Library & Package"
description: "Official Python client for SerpApi search data in applications, AI workflows, RAG, and data pipelines."
---

Integrate search data into your AI workflow, RAG or fine-tuning pipeline, Python application, or data product using the official wrapper for [SerpApi](https://serpapi.com).

SerpApi supports Google, Google Maps, Google Shopping, Bing, DuckDuckGo, Baidu, Yandex, Yahoo, eBay, YouTube, App Stores, Walmart, Home Depot, Naver, and many more engines.

Query a wide range of data at scale, including web search results, local business listings, shopping results, flight schedules, stock market data, job listings, trends, news headlines, AI Overview results, and video search results.

## Install

:::{.panel-tabset}

## pip

```bash
pip install serpapi
```

## uv

```bash
uv add serpapi
```

:::

Python 3.6 or newer is required by the package.

## First Request

Sign up at [SerpApi](https://serpapi.com/users/sign_up), copy your API key from the [dashboard](https://serpapi.com/manage-api-key), and set it in your shell:

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

The `results` variable contains a `SerpResults` object. It behaves like a standard dictionary and adds convenience helpers for response conversion, pagination, and fetching search archives.

Request parameters map directly to the SerpApi HTTP API. For the full engine list and engine-specific parameters, use the [SerpApi API documentation](https://serpapi.com/search-api). Use the [SerpApi Playground](https://serpapi.com/playground) to build and test a request before moving it into Python.

:::{.docs-home-nav}

:::{.docs-home-nav__intro}

## Documentation Map

Choose the path that matches what you are building. Start with setup and a first request, then move into client behavior, request parameters, pagination, error handling, or engine-specific examples.

- New integrations: read [Getting Started](user-guide/getting-started.md), then [Client Usage](user-guide/client-usage.md).
- Existing `google-search-results` users: follow the [Migration Guide](user-guide/migrating-from-google-search-results.md).
- Engine setup: use [Parameters and Engines](user-guide/parameters-and-engines.md) with the [SerpApi Playground](https://serpapi.com/playground).
- Production workflows: review [pagination](user-guide/pagination.md), [timeouts and errors](user-guide/errors-and-timeouts.md), [request options](user-guide/request-options.md), [account/location helpers](user-guide/account-and-locations.md), [async search archive](user-guide/async-search-archive.md), [JSON Restrictor](user-guide/json-restrictor.md), and [zero trace controls](user-guide/zero-trace.md).
- [Examples](docs/examples/google-across-countries.md): browse focused recipes for search, maps, shopping, flights, finance, trends, AI Overview, news, jobs, and YouTube.

<div class="docs-home-actions">
  <a href="user-guide/getting-started.md">Getting Started</a>
  <a href="user-guide/client-usage.md">Client Usage</a>
  <a href="user-guide/migrating-from-google-search-results.md">Migration Guide</a>
  <a href="docs/examples/google-across-countries.md">Examples</a>
  <a href="https://serpapi.com/playground">SerpApi Playground</a>
</div>

:::

:::{.docs-home-nav__sidebar}

### User Guide

- [Getting Started](user-guide/getting-started.md)
- [Client Usage](user-guide/client-usage.md)
- [Parameters and Engines](user-guide/parameters-and-engines.md)
- [Pagination](user-guide/pagination.md)
- [Errors and Timeouts](user-guide/errors-and-timeouts.md)
- [Account and Locations](user-guide/account-and-locations.md)

### Migration

- [Migrating from google-search-results](user-guide/migrating-from-google-search-results.md)

### Advanced Usage

- [Async Search Archive](user-guide/async-search-archive.md)
- [Parallel Requests with Threads](user-guide/threading.md)
- [Parallel Requests with Multiprocessing](user-guide/multiprocessing.md)
- [Zero Trace and Cache Controls](user-guide/zero-trace.md)
- [JSON Restrictor](user-guide/json-restrictor.md)
- [Request Options](user-guide/request-options.md)

### Examples

- [Google Across Countries](docs/examples/google-across-countries.md)
- [Bing Search](docs/examples/bing-search.md)
- [Google Maps Local Business](docs/examples/google-maps-local-business.md)
- [Google Shopping Products](docs/examples/google-shopping-products.md)
- [Google Flights Travel](docs/examples/google-flights-travel.md)
- [Google Finance Market Data](docs/examples/google-finance-market-data.md)
- [Google Trends Demand](docs/examples/google-trends-demand.md)
- [Google AI Overview](docs/examples/google-ai-overview.md)
- [Google News Monitoring](docs/examples/google-news-monitoring.md)
- [Google Jobs Listings](docs/examples/google-jobs-listings.md)
- [YouTube Video Search](docs/examples/youtube-video-search.md)

:::

:::
