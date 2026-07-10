---
title: "Google Shopping Products"
description: "Search Google Shopping and extract product cards."
---

# Google Shopping Products

Use the Google Shopping API when you need product result cards, prices, merchants, and shopping links. It is a good fit for product discovery, price monitoring, catalog enrichment, and market research.

## Search Products

```python
import os
import serpapi


client = serpapi.Client(api_key=os.environ["SERPAPI_KEY"], timeout=20)

results = client.search(
    engine="google_shopping",
    q="espresso machine",
    location="Austin, Texas",
    gl="us",
    hl="en",
)

for product in results.get("shopping_results", [])[:5]:
    print(product.get("title"))
    print(product.get("price"), product.get("source"))
    print(product.get("link"))
```

## What to Read

Most shopping workflows use `shopping_results`. Save `title`, `price`, `source`, `rating`, `reviews`, `thumbnail`, and `link` if present. For filtering, sorting, and engine-specific options, check the live docs before hard-coding parameters.

See the [Google Shopping API documentation](https://serpapi.com/google-shopping-api) and experiment in the [SerpApi Playground](https://serpapi.com/playground).
