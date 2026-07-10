---
title: "Baidu Search"
description: "Search Baidu results for China-focused research workflows."
---

# Baidu Search

Use the Baidu Search API when your application needs results from Baidu's web index. It is useful for China-focused SEO checks, market research, and search result monitoring.

## Search Baidu

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

## What to Read

Start with `organic_results`, then inspect any top-level result blocks returned by the query. Baidu result shapes can vary by keyword, so store only fields you have observed in sample responses.

See the [Baidu Search API documentation](https://serpapi.com/baidu-search-api) for supported filters.
