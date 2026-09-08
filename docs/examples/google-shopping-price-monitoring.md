---
title: "Google Shopping Price Monitoring"
description: "Filter Google Shopping listings by price and read selected product fields."
---

# Google Shopping Price Monitoring

Filter Google Shopping listings by price to compare offers from different merchants. The example searches for espresso machines priced between 100 and 800 in the search's currency.

## Search Filtered Products

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

## Read the Results

Read product listings from `shopping_results`. Useful fields include `title`, `product_id`, `price`, `extracted_price`, `source`, `rating`, `reviews`, `thumbnail`, `delivery`, `product_link`, and `serpapi_immersive_product_api`.

Use `min_price`, `max_price`, `sort_by`, `free_shipping`, and `on_sale` to filter and order offers. To fetch more pages, use `serpapi_pagination.next` when it is present. The example limits response fields with `json_restrictor`. Include `serpapi_pagination` in that selector if you need pagination. See the [Google Shopping API documentation](https://serpapi.com/google-shopping-api) for the full parameter set.
