---
title: "Google Play Store Apps"
description: "Search Google Play app results and read app store metadata."
---

# Google Play Store Apps

Use the Google Play Store API when you need app search results, app metadata, ratings, or links into Google Play.

## Search Apps

```python
import os
import serpapi


client = serpapi.Client(api_key=os.environ["SERPAPI_KEY"], timeout=20)

results = client.search(
    engine="google_play",
    q="kite",
    store="apps",
    max_results="2",
)

for app in results.get("organic_results", [])[:5]:
    print(app.get("title"))
    print(app.get("rating"), app.get("downloads"))
    print(app.get("link"))
```

## What to Read

Start with `organic_results`. Useful fields include `title`, `link`, `rating`, `downloads`, `description`, `thumbnail`, and app identifiers.

See the [Google Play Store API documentation](https://serpapi.com/google-play-api) for store, device, and localization options.
