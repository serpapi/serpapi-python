---
title: "Google Across Countries"
description: "Run the same Google Search across multiple countries and locations."
---

# Google Across Countries

Use `gl`, `hl`, `location`, and sometimes `google_domain` to compare localized Google results.

## Compare Several Countries

```python
import os
import serpapi


client = serpapi.Client(api_key=os.environ["SERPAPI_KEY"], timeout=20)

markets = [
    {"name": "United States", "gl": "us", "hl": "en", "location": "Austin, Texas"},
    {"name": "United Kingdom", "gl": "gb", "hl": "en", "location": "London, England"},
    {"name": "France", "gl": "fr", "hl": "fr", "location": "Paris, France"},
    {"name": "Germany", "gl": "de", "hl": "de", "location": "Berlin, Germany"},
    {"name": "India", "gl": "in", "hl": "en", "location": "Mumbai, Maharashtra"},
]

for market in markets:
    results = client.search({
        "engine": "google",
        "q": "best coffee beans",
        "location": market["location"],
        "gl": market["gl"],
        "hl": market["hl"],
    })

    organic = results.get("organic_results", [])
    first = organic[0] if organic else {}

    print(market["name"])
    print(first.get("title"))
    print(first.get("link"))
    print()
```

## Use a Google Domain

Some workflows also need a specific Google domain:

```python
results = client.search({
    "engine": "google",
    "q": "best coffee beans",
    "google_domain": "google.co.in",
    "gl": "in",
    "hl": "en",
    "location": "Mumbai, Maharashtra",
})
```

## Finding Valid Locations

Use the client helper:

```python
locations = client.locations(q="Mumbai", limit=5)

for location in locations:
    print(location.get("canonical_name"))
```

See [Account and Locations](../../user-guide/account-and-locations.md) for the local guide to the locations helper. Use the [SerpApi Playground](https://serpapi.com/playground) to test location values with the rest of your search parameters.
