---
title: "Google Finance Market Data"
description: "Fetch quote, graph, and market context from Google Finance."
---

# Google Finance Market Data

Use the Google Finance API for stock, index, mutual fund, currency, or futures lookups. It is useful for dashboards, watchlists, and enriching business workflows with current market context.

## Fetch a Quote

```python
import os
import serpapi


client = serpapi.Client(api_key=os.environ["SERPAPI_KEY"], timeout=20)

results = client.search({
    "engine": "google_finance",
    "q": "GOOGL:NASDAQ",
    "window": "1M",
    "hl": "en",
})

summary = results.get("summary", {})
knowledge = results.get("knowledge_graph", {})

print(summary.get("title") or knowledge.get("title"))
print(summary.get("price") or knowledge.get("price"))
print("Graph points:", len(results.get("graph", [])))
```

## What to Read

Use `summary` and `knowledge_graph` for quote-level details, `graph` for time-series points, and `news_results` for finance-related headlines when present. Use `window` to change the graph range.

See the [Google Finance API documentation](https://serpapi.com/google-finance-api) for supported `q` formats and time windows. You can test symbols in the [SerpApi Playground](https://serpapi.com/playground).

