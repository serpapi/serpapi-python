---
title: "Home Depot Product Search"
description: "Search Home Depot product cards and read price, rating, and product identifiers."
---

# Home Depot Product Search

Use The Home Depot Search API for home improvement product discovery, price tracking, and catalog enrichment. Start with a broad query and then add filters once you know the category shape.

## Search Products

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

## What to Read

Start with `products`. Useful fields include `title`, `product_id`, `price`, `rating`, `reviews`, `brand`, `thumbnail`, and product URLs when present.

See the [The Home Depot Search API documentation](https://serpapi.com/home-depot-search-api) for product filters and pagination.
