---
title: "DuckDuckGo Search"
description: "Run a DuckDuckGo search and read organic result fields."
---

# DuckDuckGo Search

Use the DuckDuckGo Search API when you need another privacy-oriented web result source alongside Google and Bing. Start with a simple query, then add region and time filters when your workflow needs them.

## Search DuckDuckGo

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

## What to Read

Most workflows start with `organic_results`. Useful fields include `title`, `link`, `snippet`, `position`, and any rich result blocks returned for the query.

See the [DuckDuckGo Search API documentation](https://serpapi.com/duckduckgo-search-api) for region, date, and safe-search options.
