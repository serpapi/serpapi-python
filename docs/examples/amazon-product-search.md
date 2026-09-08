---
title: "Amazon Product Search"
description: "Search Amazon products and read prices, ratings, delivery details, and product IDs."
---

# Amazon Product Search

Search Amazon for product listings, prices, ratings, delivery details, and sponsored products. Set `k` to the text you want to search for.

## Search Products

[Install the package and set your API key](../user_guide/getting-started.md#installation) before running this example.

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

## Read the Results

Read product listings from `organic_results`. The `asin` field is Amazon's product ID. Useful fields include `title`, `asin`, `price`, `extracted_price`, `rating`, `reviews`, `thumbnail`, `delivery`, `prime`, `link_clean`, and `serpapi_link`. Some searches also return `product_ads`, `featured_products`, `video_results`, `filters`, and `related_searches`.

For country settings, sorting, product categories, and filters, see the [Amazon Search API documentation](https://serpapi.com/amazon-search-api). Use the [SerpApi Playground](https://serpapi.com/playground) to inspect the response fields for your product category.
