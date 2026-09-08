---
title: "DuckDuckGo Search"
description: "Run a DuckDuckGo search and read web result fields."
---

# DuckDuckGo Search

Search DuckDuckGo to read its web results or compare them with Google and Bing. You can narrow the search with region and time filters.

## Search DuckDuckGo

[Install the package and set your API key](../user_guide/getting-started.md#installation) before running this example.

```python
import os
import serpapi


client = serpapi.Client(api_key=os.environ["SERPAPI_KEY"], timeout=20)

results = client.search(
    engine="duckduckgo",
    q="coffee",
)

for result in results.get("organic_results", [])[:5]:
    print(result.get("position"), result.get("title"))
    print(result.get("link"))
```

## Read the Results

Read web listings from `organic_results`. Each listing can include `title`, `link`, `snippet`, and `position`. Inspect the response for other sections returned by your query.

See the [DuckDuckGo Search API documentation](https://serpapi.com/duckduckgo-search-api) for region, date, and safe-search options.
