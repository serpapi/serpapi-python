---
title: "Bing Search"
description: "Run a Bing web search and read organic result fields."
---

# Bing Search

Use the Bing Search API when you want a second web index alongside Google, or when your product specifically needs Bing result ordering. The Python client sends Bing parameters directly to SerpApi, so you can start with a small query and add localization or pagination as your use case grows.

## Search Bing

```python
import os
import serpapi


client = serpapi.Client(api_key=os.environ["SERPAPI_KEY"], timeout=20)

results = client.search(
    engine="bing",
    q="coffee",
    location="Austin, Texas",
)

for result in results.get("organic_results", [])[:5]:
    print(result.get("position"), result.get("title"))
    print(result.get("link"))
```

## What to Read

Most applications start with `organic_results`, then store the `title`, `link`, `snippet`, and `position` fields. If your query returns richer SERP blocks, inspect the top-level keys with:

```python
print(results.keys())
```

For every supported Bing parameter, use the [Bing Search API documentation](https://serpapi.com/bing-search-api). To tune a query interactively, use the [SerpApi Playground](https://serpapi.com/playground).
