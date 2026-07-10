---
title: "Walmart Product Search"
description: "Search Walmart products and read pricing, reviews, shipping, and product IDs."
---

# Walmart Product Search

Use the Walmart Search API for product search, price monitoring, catalog enrichment, and availability checks. Walmart uses `query` instead of `q`.

## Search Products

```python
import os
import serpapi


client = serpapi.Client(api_key=os.environ["SERPAPI_KEY"], timeout=20)

results = client.search(
    engine="walmart",
    query="coffee maker",
    walmart_domain="walmart.com",
)

for product in results.get("organic_results", [])[:5]:
    offer = product.get("primary_offer", {})
    print(product.get("title"))
    print(offer.get("offer_price"), product.get("rating"), product.get("reviews"))
    print(product.get("us_item_id"), product.get("product_page_url"))
```

## What to Read

Start with `organic_results`. Useful fields include `title`, `us_item_id`, `product_id`, `rating`, `reviews`, `seller_name`, `primary_offer.offer_price`, `price_per_unit`, `out_of_stock`, `product_page_url`, and `serpapi_product_page_url`.

Use `sort`, `min_price`, `max_price`, `store_id`, and `facet` when you need more targeted product monitoring. See the [Walmart Search API documentation](https://serpapi.com/walmart-search-api) for supported filters and pagination behavior.
