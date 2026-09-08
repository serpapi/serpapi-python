---
title: "Google Play Store Apps"
description: "Search Google Play for apps and read their titles, ratings, and links."
---

# Google Play Store Apps

Search Google Play for apps and read their ratings, descriptions, and store links.

## Search Apps

[Install the package and set your API key](../user_guide/getting-started.md#installation) before running this example.

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

## Read the Results

Read app listings from `organic_results`. Useful fields include `title`, `link`, `rating`, `downloads`, `description`, `thumbnail`, and app identifiers.

See the [Google Play Store API documentation](https://serpapi.com/google-play-api) for store, device, and localization options.
