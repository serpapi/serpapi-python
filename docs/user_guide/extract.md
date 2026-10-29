---
title: "Extract API"
description: "Extract page content, discover URLs, and crawl websites with the Python client."
---

# Extract API

Use `client.extract()` to read content from a public URL. It supports single-page scraping, URL discovery, and crawling. Pass a parameter dictionary or keyword arguments, as you would with `client.search()`. The client sets `engine="extract"` automatically.

See the [Extract API documentation](https://serpapi.com/extract-api) for all parameters and response fields.

## Get Page Content as Markdown

Set `output="md"` to get the page's main content as a Markdown string.

After [setting your API key](getting-started.md#installation), run:

```python
import os
import serpapi

client = serpapi.Client(api_key=os.environ["SERPAPI_KEY"], timeout=60)
markdown = client.extract(
    url="https://serpapi.com/",
    output="md",
)

print(markdown)
```

You can pass the returned string to an AI agent or save it to a file.

## Get Structured Data as JSON

JSON is the default output format. The SDK returns a dictionary-like `SerpResults` object with page information, meta tags, structured data, links, images, and Markdown. The sections returned depend on the target page.

```python
results = client.extract(url="https://serpapi.com/")

print(results["page_information"]["title"])
print(results["markdown"])
```

The `markdown` field contains the page's main content. Set `include_markdown=False` to omit it from the JSON response.

The module-level `serpapi.extract(url=..., api_key=...)` function accepts the same parameters.

## Get HTML

Set `output="html"` to get the retrieved HTML as a string:

```python
html = client.extract(url="https://serpapi.com/", output="html")
```

## Discover URLs

Set `mode="map"` to discover URLs on a website:

```python
results = client.extract(
    url="https://serpapi.com/",
    mode="map",
    include_sitemap=False,
    include_subdomains=False,
)

for entry in results["urls"]:
    print(entry["url"])
```

Map mode includes sitemap URLs by default. Set `include_sitemap=False` to discover URLs from the page's links only. Set `include_subdomains=True` to include subdomains.

## Crawl Multiple Pages

Set `mode="crawl"` to follow links and extract pages:

```python
results = client.extract(
    url="https://serpapi.com/",
    mode="crawl",
    max_pages=2,
    max_depth=1,
    timeout=180,
)

for page in results["pages"]:
    print(page["url"])
    print(page["markdown"])
```

Each entry in `results["pages"]` contains the extracted page's data, including its `markdown` field. The starting page has depth `0`. `max_pages` includes the starting page and defaults to `10`. Each successfully extracted page can consume one search credit. Set a page limit for your crawl and allow enough time for the HTTP request to finish.

For requests you want to retrieve later, pass `"async": True` in a parameter dictionary and use the [Search Archive](async-search-archive.md).

## Timeouts and Content Filters

The `timeout=` keyword sets the SDK's HTTP timeout in seconds. Set it above the API fetch timeout, and allow time for all pages when crawling. Put the Extract API's fetch timeout in the parameter dictionary to send it in milliseconds:

```python
results = client.extract(
    {"url": "https://serpapi.com/", "timeout": 30000},
    timeout=60,
)
```

Use `include_tags` and `exclude_tags` to keep or remove content with CSS selectors, such as `include_tags="article, main"` or `exclude_tags="nav, footer"`. See the [Extract API parameters](https://serpapi.com/extract-api) for details and [Errors and Timeouts](errors-and-timeouts.md) for exception handling.
