---
title: "eBay Product Listings"
description: "Search eBay listings and read product, price, and seller fields."
---

# eBay Product Listings

Use the eBay Search API when you need marketplace listings, prices, condition data, or seller result pages. eBay uses `_nkw` for the search keyword.

## Search eBay

```python
import os
import serpapi


client = serpapi.Client(api_key=os.environ["SERPAPI_KEY"], timeout=20)

results = client.search(
    engine="ebay",
    _nkw="coffee",
)

for listing in results.get("organic_results", [])[:5]:
    print(listing.get("title"))
    print(listing.get("price"), listing.get("condition"))
    print(listing.get("link"))
```

## What to Read

Start with `organic_results`. Useful fields include `title`, `price`, `condition`, `shipping`, `location`, `seller`, `thumbnail`, and `link`.

See the [eBay Search API documentation](https://serpapi.com/ebay-search-api) for filters, sorting, and pagination.
