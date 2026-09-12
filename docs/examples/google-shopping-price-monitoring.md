---
title: "Google Shopping Price Monitoring"
description: "Compare US espresso-machine listings within a budget."
---

# Google Shopping Price Monitoring

Search Google Shopping for a De'Longhi Stilosa espresso machine in Austin, Texas, and compare offers priced from $100 to $200. The example filters the returned prices in Python using the numeric `extracted_price` field.

## Search Filtered Products

[Install the package and set your API key](../user_guide/getting-started.md#installation) before running this example.

```python
import os
import serpapi


client = serpapi.Client(api_key=os.environ["SERPAPI_KEY"], timeout=20)

results = client.search(
    engine="google_shopping",
    q="DeLonghi Stilosa espresso machine",
    location="Austin, Texas",
    gl="us",
    hl="en",
    json_restrictor="error, shopping_results[].{title, price, extracted_price, source, rating, reviews, product_link}",
)

for product in results.get("shopping_results", []):
    price = product.get("extracted_price")
    if price is None or not 100 <= price <= 200:
        continue
    print(product.get("title"))
    print(product.get("price"), product.get("source"))
    print(product.get("rating"), product.get("reviews"))
```

## Read the Results

Read product listings from `shopping_results`. Useful fields include `title`, `product_id`, `price`, `extracted_price`, `source`, `rating`, `reviews`, `thumbnail`, `delivery`, `product_link`, and `serpapi_immersive_product_api`.

The example limits response fields with `json_restrictor` and keeps `error` so API errors remain visible. Use `extracted_price` for numeric comparisons and `price` for display. See the [Google Shopping API documentation](https://serpapi.com/google-shopping-api) for the full parameter set.
