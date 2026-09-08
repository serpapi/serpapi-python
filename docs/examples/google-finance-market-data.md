---
title: "Google Finance Market Data"
description: "Read prices, charts, and related news from Google Finance."
---

# Google Finance Market Data

Look up stocks, indexes, mutual funds, currencies, and futures on Google Finance. You can use the returned prices and charts in a watchlist or dashboard.

## Fetch a Quote

[Install the package and set your API key](../user_guide/getting-started.md#installation) before running this example.

```python
import os
import serpapi


client = serpapi.Client(api_key=os.environ["SERPAPI_KEY"], timeout=20)

results = client.search(
    engine="google_finance",
    q="GOOGL:NASDAQ",
    window="1M",
    hl="en",
)

summary = results.get("summary", {})
knowledge = results.get("knowledge_graph", {})

print(summary.get("title") or knowledge.get("title"))
print(summary.get("price") or knowledge.get("price"))
print("Graph points:", len(results.get("graph", [])))
```

## Read the Results

Read the name and price from `summary` or `knowledge_graph`, depending on the response. The `graph` list contains values over time, and `news_results` contains related headlines when available. Set `window` to choose the chart's time range.

See the [Google Finance API documentation](https://serpapi.com/google-finance-api) for supported `q` formats and time windows. You can test symbols in the [SerpApi Playground](https://serpapi.com/playground).
