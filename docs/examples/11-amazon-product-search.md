---
title: "Amazon Product Search"
description: "Search Amazon products and read price, rating, delivery, and product identifiers."
---

# Amazon Product Search

Use the Amazon Search API when you need product listings, prices, ratings, delivery details, sponsored products, or Amazon product identifiers. The Amazon engine uses `k` for the search query.

## Search Products

```python
import os
import serpapi


client = serpapi.Client(api_key=os.environ["SERPAPI_KEY"], timeout=20)

results = client.search(
    engine="amazon",
    k="coffee grinder",
    amazon_domain="amazon.com",
)

for product in results.get("organic_results", [])[:5]:
    print(product.get("title"))
    print(product.get("price"), product.get("rating"), product.get("reviews"))
    print(product.get("asin"), product.get("link_clean"))
```

## What to Read

Start with `organic_results` for product cards. Useful fields include `title`, `asin`, `price`, `extracted_price`, `rating`, `reviews`, `thumbnail`, `delivery`, `prime`, `link_clean`, and `serpapi_link`. Some searches also return `product_ads`, `featured_products`, `video_results`, `filters`, and `related_searches`.

For localization, sorting, category nodes, and Amazon-specific filters, see the [Amazon Search API documentation](https://serpapi.com/amazon-search-api). Use the [SerpApi Playground](https://serpapi.com/playground) to inspect result shapes for the product category you care about.
