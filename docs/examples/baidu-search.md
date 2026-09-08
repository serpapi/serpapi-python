---
title: "Baidu Search"
description: "Search Baidu and read web results for research about China."
---

# Baidu Search

Search Baidu for web pages, for example to research a market in China or check where a website appears in search results.

## Search Baidu

[Install the package and set your API key](../user_guide/getting-started.md#installation) before running this example.

```python
import os
import serpapi


client = serpapi.Client(api_key=os.environ["SERPAPI_KEY"], timeout=20)

results = client.search(
    engine="baidu",
    q="coffee",
)

for result in results.get("organic_results", [])[:5]:
    print(result.get("position"), result.get("title"))
    print(result.get("link"))
```

## Read the Results

Read web listings from `organic_results`. The response may contain other sections depending on the query. Inspect a sample response to see which fields are available before choosing what to store.

See the [Baidu Search API documentation](https://serpapi.com/baidu-search-api) for supported filters.
