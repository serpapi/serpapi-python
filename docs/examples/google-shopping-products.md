---
title: "Google Shopping Products"
description: "Search Google Shopping and read product listings."
---

# Google Shopping Products

Search Google Shopping for products, prices, merchants, and product links. Use the results to compare prices, research products, or add merchant information to a product catalog.

## Search Products

[Install the package and set your API key](../user_guide/getting-started.md#installation) before running this example.

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

## Read the Results

Read product listings from `shopping_results`. Save `title`, `price`, `source`, `rating`, `reviews`, `thumbnail`, and `link` if present. Check the API documentation for supported filters and sorting options before adding them to your request.

See the [Google Shopping API documentation](https://serpapi.com/google-shopping-api) and experiment in the [SerpApi Playground](https://serpapi.com/playground).
