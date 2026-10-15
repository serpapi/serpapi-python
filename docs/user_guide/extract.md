---
title: "Extract API"
description: "Extract page content, discover URLs, and crawl websites with the Python client."
---

# Extract API

Use `client.extract()` to read content from a public URL. It supports single-page scraping, URL discovery, and crawling. Pass a parameter dictionary or keyword arguments, as you would with `client.search()`. The client sets `engine="extract"` automatically.

See the [Extract API documentation](https://serpapi.com/extract-api) for all parameters and response fields.

## Get Only the Page Content as JSON

Set `include_markdown=True` and `json_restrictor="text_content.markdown"` to get the page's Markdown content in a JSON response. This removes metadata and all other response sections.

After [setting your API key](getting-started.md#installation), run:

```python
import os
import serpapi

client = serpapi.Client(api_key=os.environ["SERPAPI_KEY"], timeout=60)
results = client.extract(
    url="https://example.com/",
    output="json",
    include_markdown=True,
    json_restrictor="text_content.markdown",
)

markdown = results["text_content"]["markdown"]
print(markdown)
```

The response has this structure, with the extracted page content in `markdown`:

```json
{
  "text_content": {
    "markdown": "Page content in Markdown..."
  }
}
```

The SDK returns a dictionary-like `SerpResults` object. Read `results["text_content"]["markdown"]` to get the plain Markdown string, as shown above. You can pass that string to an AI agent or save it to a file.

See [JSON Restrictor](json-restrictor.md) for other ways to select response fields.

## Get the Full Extract Response

Leave out `json_restrictor` to receive the available extracted sections, such as page information, headings, links, and text content:

```python
results = client.extract(
    url="https://example.com/",
    include_markdown=True,
)

print(results["page_information"]["title"])
print(results["text_content"]["markdown"])
```

JSON is the default output format. `include_markdown=True` adds Markdown under `text_content`; the rest of the response remains JSON. The sections returned depend on the target page.

The module-level `serpapi.extract(url=..., api_key=...)` function accepts the same parameters.

## Markdown and HTML Responses

Use `output="md"` or `output="html"` to receive a Python string:

```python
markdown_response = client.extract(url="https://example.com/", output="md")
html = client.extract(url="https://example.com/", output="html")
```

For a scraped page, `output="md"` includes search metadata before the page content. Use the [content-only JSON example](#get-only-the-page-content-as-json) when you want the page's Markdown without those extra sections. `output="html"` returns the retrieved HTML.

## Discover URLs

Set `mode="map"` to discover URLs on a website:

```python
results = client.extract(
    url="https://www.python.org/",
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
    url="https://www.python.org/",
    mode="crawl",
    max_pages=2,
    max_depth=1,
    timeout=180,
)

for page in results["pages"]:
    print(page["url"])
```

The starting page has depth `0`. `max_pages` includes the starting page and defaults to `10`. Each successfully extracted page can consume one search credit. Set a page limit for your crawl and allow enough time for the HTTP request to finish. For requests you want to retrieve later, pass `"async": True` in a parameter dictionary and use the [Search Archive](async-search-archive.md).

## Timeouts and Content Filters

The `timeout=` keyword sets the SDK's HTTP timeout in seconds. Set it above the API fetch timeout, and allow time for all pages when crawling. Put the Extract API's fetch timeout in the parameter dictionary to send it in milliseconds:

```python
results = client.extract(
    {"url": "https://example.com/", "timeout": 30000},
    timeout=60,
)
```

Use `include_tags` and `exclude_tags` to keep or remove content with CSS selectors, such as `include_tags="article, main"` or `exclude_tags="nav, footer"`. See the [Extract API parameters](https://serpapi.com/extract-api) for details and [Errors and Timeouts](errors-and-timeouts.md) for exception handling.
