---
title: "Home Depot Product Search"
description: "Search Home Depot products and read prices, ratings, and product IDs."
---

# Home Depot Product Search

Search The Home Depot for home improvement products. You can use the listings to track prices or add product details to a catalog. Inspect the response for your query before adding category filters.

## Search Products

[Install the package and set your API key](../user_guide/getting-started.md#installation) before running this example.

```python
import os
import serpapi


client = serpapi.Client(api_key=os.environ["SERPAPI_KEY"], timeout=20)

results = client.search(
    engine="home_depot",
    q="table",
)

for product in results.get("products", [])[:5]:
    print(product.get("title"))
    print(product.get("price"), product.get("rating"))
    print(product.get("product_id"))
```

## Read the Results

Read product listings from `products`. Useful fields include `title`, `product_id`, `price`, `rating`, `reviews`, `brand`, `thumbnail`, and product URLs when present.

See [The Home Depot Search API documentation](https://serpapi.com/home-depot-search-api) for product filters and pagination.
