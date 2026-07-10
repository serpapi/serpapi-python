---
title: "Google Shopping Price Monitoring"
description: "Filter Google Shopping results by price and read product cards for monitoring workflows."
---

# Google Shopping Price Monitoring

Use the Google Shopping API when you need product cards from many merchants. For price monitoring, combine query, market, price filters, and selected result fields.

## Search Filtered Products

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
    min_price=100,
    max_price=800,
    sort_by=1,
    json_restrictor="shopping_results[].{title, price, source, rating, reviews, link}",
)

for product in results.get("shopping_results", [])[:5]:
    print(product.get("title"))
    print(product.get("price"), product.get("source"))
    print(product.get("rating"), product.get("reviews"))
```

## What to Read

Start with `shopping_results`. Useful fields include `title`, `product_id`, `price`, `extracted_price`, `source`, `rating`, `reviews`, `thumbnail`, `delivery`, `product_link`, and `serpapi_immersive_product_api`.

Use `min_price`, `max_price`, `sort_by`, `free_shipping`, and `on_sale` for monitoring workflows. For pagination, prefer `serpapi_pagination.next` over hand-built offsets when it is present. See the [Google Shopping API documentation](https://serpapi.com/google-shopping-api) for the full parameter set.
