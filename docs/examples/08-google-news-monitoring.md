---
title: "Google News Monitoring"
description: "Collect recent headlines for a topic with Google News."
---

# Google News Monitoring

Use the Google News API for media monitoring, topic tracking, and alerting workflows. It returns news-focused result cards instead of general web results.

## Search News

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

## What to Read

Start with `news_results`. Save `title`, `link`, `source`, `date`, `snippet`, and `thumbnail` when present. News result shapes can vary by query, so inspect a sample response before deciding your storage schema.

See the [Google News API documentation](https://serpapi.com/google-news-api) and tune your topic in the [SerpApi Playground](https://serpapi.com/playground).
