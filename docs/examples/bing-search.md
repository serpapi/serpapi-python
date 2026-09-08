---
title: "Bing Search"
description: "Run a Bing web search and read result titles, links, and positions."
---

# Bing Search

Search Bing to read its web results or compare them with Google results. The example below searches for coffee from Austin, Texas. You can add language, location, and pagination parameters to the same request.

## Search Bing

[Install the package and set your API key](../user_guide/getting-started.md#installation) before running this example.

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

## Read the Results

Read web listings from `organic_results`. Each listing can include a `title`, `link`, `snippet`, and `position`. To see which other sections the response contains, print its keys:

```python
print(results.keys())
```

For all supported Bing parameters, see the [Bing Search API documentation](https://serpapi.com/bing-search-api). To try different parameters in your browser, use the [SerpApi Playground](https://serpapi.com/playground).
