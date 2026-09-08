---
title: "Google News Monitoring"
description: "Collect recent headlines for a topic with Google News."
---

# Google News Monitoring

Search Google News for articles about a topic. You can collect headlines over time or use new matches to trigger alerts.

## Search News

[Install the package and set your API key](../user_guide/getting-started.md#installation) before running this example.

```python
import os
import serpapi


client = serpapi.Client(api_key=os.environ["SERPAPI_KEY"], timeout=20)

results = client.search(
    engine="google_news",
    q="artificial intelligence",
    gl="us",
    hl="en",
)

for item in results.get("news_results", [])[:5]:
    print(item.get("title"))
    print(item.get("source", {}).get("name") or item.get("source"))
    print(item.get("link"))
```

## Read the Results

Read articles from `news_results`. Save `title`, `link`, `source`, `date`, `snippet`, and `thumbnail` when present. Response fields vary by query, so inspect a sample response before choosing which fields to store.

See the [Google News API documentation](https://serpapi.com/google-news-api) and try your topic in the [SerpApi Playground](https://serpapi.com/playground).
