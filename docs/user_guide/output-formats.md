---
title: "Output Formats"
description: "Choose JSON, Markdown, or HTML results with the output parameter."
---

# Output Formats

Set `output` on `client.search()` to choose the response format. JSON is the default.

| `output` | Python return type | Use |
| --- | --- | --- |
| `"json"` | `serpapi.SerpResults` | Read individual fields, such as titles and links, and fetch more pages. |
| `"md"` | `str` | Give Markdown search results to AI agents and language models. |
| `"html"` | `str` | Inspect the search results as HTML. |

## JSON

JSON stores results as named fields and lists. Use it when your code needs to read individual values, such as a result's title or link.

After [setting your API key](getting-started.md#installation), create a client and run a search:

```python
import os
import serpapi

client = serpapi.Client(api_key=os.environ["SERPAPI_KEY"])
results = client.search(engine="google", q="coffee", output="json")

for result in results.get("organic_results", []):
    print(result.get("title"), result.get("link"))
```

You can leave out `output="json"` because JSON is the default. `SerpResults` behaves like a dictionary and provides `as_dict()`, `next_page()`, and `yield_pages()`. The loop above uses an empty list if `organic_results` is missing. See [Pagination](pagination.md) for examples that fetch more pages.

## Markdown

Use `output="md"` for search results formatted with headings, links, and tables:

```python
markdown = client.search(engine="google", q="coffee", output="md")
print(markdown[:500])
```

The client returns a plain Python string. The example prints its first 500 characters. You can pass the full string to an AI agent as the result of a search tool. See [AI Agents](../ai-agents.md) for integrations and [SerpApi's Markdown output guide](https://serpapi.com/markdown-output) for API details.

## HTML

Use `output="html"` to retrieve the HTML of the original search results page:

```python
html = client.search(engine="google", q="coffee", output="html")
print(html[:500])
```

The client returns HTML as a string. Use JSON when you need to read named result fields or call pagination methods such as `next_page()`. These methods are available on `SerpResults`, and cannot be called on an HTML or Markdown string.

The same `output` values are supported by `client.search_archive()` when retrieving a saved search. See [Async Search Archive](async-search-archive.md).
