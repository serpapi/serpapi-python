---
title: "eBay Product Listings"
description: "Search eBay listings and read product, price, and seller fields."
---

# eBay Product Listings

Search eBay for listings with prices, item conditions, and seller information. Set `_nkw` to your search text.

## Search eBay

[Install the package and set your API key](../user_guide/getting-started.md#installation) before running this example.

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

## Read the Results

Read the listings from `organic_results`. Useful fields include `title`, `price`, `condition`, `shipping`, `location`, `seller`, `thumbnail`, and `link`.

See the [eBay Search API documentation](https://serpapi.com/ebay-search-api) for filters, sorting, and pagination.
