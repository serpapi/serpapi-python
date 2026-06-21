---
title: "SerpApi Python Library & Package"
description: "Official Python client for SerpApi search data in applications, AI workflows, RAG, and data pipelines."
---

Integrate search data into your AI workflow, RAG or fine-tuning pipeline, Python application, or data product using the official wrapper for [SerpApi](https://serpapi.com).

SerpApi supports Google, Google Maps, Google Shopping, Bing, DuckDuckGo, Baidu, Yandex, Yahoo, eBay, YouTube, App Stores, Walmart, Home Depot, Naver, and many more engines.

Query a wide range of data at scale, including web search results, local business listings, shopping results, flight schedules, stock market data, job listings, trends, news headlines, AI Overview results, and video search results.

This package is separate from the deprecated `google-search-results` SDK. This package is maintained by SerpApi and is the recommended Python package for new integrations. If your project still depends on `google-search-results`, see [Migrating from google-search-results](user-guide/migrating-from-google-search-results.md).

## Install

With `pip`:

```bash
pip install serpapi
```

With `uv` in a project:

```bash
uv add serpapi
```

With `uv` in an existing environment:

```bash
uv pip install serpapi
```

Python 3.6 or newer is required by the package. Building this documentation site uses Great Docs and Quarto on Python 3.11 or newer.

## First Request

```python
import os
import serpapi

client = serpapi.Client(api_key=os.environ["SERPAPI_KEY"])
results = client.search({
    "engine": "google",
    "q": "coffee",
    "location": "Austin, Texas",
    "hl": "en",
    "gl": "us",
})

print(results["organic_results"][0]["link"])
```

The `results` variable contains a `SerpResults` object. It behaves like a standard dictionary and adds convenience helpers for response conversion, pagination, and fetching search archives.

Request parameters map directly to the SerpApi HTTP API. The actual full supported engine list and engine-specific parameters are maintained in the [SerpApi API documentation](https://serpapi.com/search-api). Use the [SerpApi Playground](https://serpapi.com/playground) to build a request visually, test it, and copy the final parameters into Python.

:::{.docs-home-nav}

:::{.docs-home-nav__intro}

## Documentation Map

The full guide and examples are listed here on the homepage so you can jump directly into the workflow you need. Guide pages also include the standard collapsible docs sidebar when you open them.

<div class="docs-home-actions">
  <a href="user-guide/getting-started.md">Getting Started</a>
  <a href="user-guide/client-usage.md">Client Usage</a>
  <a href="user-guide/migrating-from-google-search-results.md">Migration Guide</a>
  <a href="docs/examples/google-flights-travel.md">Travel Example</a>
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

## Where to Go Next

- Start with [Getting Started](user-guide/getting-started.md) for installation and a first request.
- Read [Client Usage](user-guide/client-usage.md) to learn the Python API, response helpers, request options, and archive helpers.
- Use [Migrating from google-search-results](user-guide/migrating-from-google-search-results.md) if your project still depends on the deprecated SDK.
- Use [Parameters and Engines](user-guide/parameters-and-engines.md) for links to the full supported engine and parameter docs.
- Browse [Examples](docs/examples/google-flights-travel.md) for focused recipes covering travel, finance, trends, AI Overview, local business, shopping, Bing, jobs, news, and video search.
- Review the generated API reference for `Client`, `SerpResults`, and exception classes.
- Use the [SerpApi Playground](https://serpapi.com/playground) to build and test request parameters before putting them in code.
