---
title: "Walmart Product Search"
description: "Search Walmart products and read prices, reviews, shipping details, and product IDs."
---

# Walmart Product Search

Search Walmart for products, prices, and availability. You can use the results to track prices or add details to a product catalog. Set `query` to your search text. This engine does not use `q`.

## Search Products

[Install the package and set your API key](../user_guide/getting-started.md#installation) before running this example.

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

## Read the Results

Read product listings from `organic_results`. Useful fields include `title`, `us_item_id`, `product_id`, `rating`, `reviews`, `seller_name`, `primary_offer.offer_price`, `price_per_unit`, `out_of_stock`, `product_page_url`, and `serpapi_product_page_url`.

Use `sort`, `min_price`, `max_price`, `store_id`, and `facet` to sort results, set price limits, or filter by store and product features. See the [Walmart Search API documentation](https://serpapi.com/walmart-search-api) for supported filters and pagination behavior.
