---
title: "Google Across Countries"
description: "Run the same Google Search across several countries and locations."
---

# Google Across Countries

Compare Google results by setting the country (`gl`), interface language (`hl`), and search location (`location`). Use `google_domain` if you need a particular Google domain.

## Compare Several Countries

[Install the package and set your API key](../user_guide/getting-started.md#installation) before running this example.

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
    results = client.search(
        engine="google",
        q="best coffee beans",
        location=market["location"],
        gl=market["gl"],
        hl=market["hl"],
    )

    organic = results.get("organic_results", [])
    first = organic[0] if organic else {}

    print(market["name"])
    print(first.get("title"))
    print(first.get("link"))
    print()
```

## Use a Google Domain

Set `google_domain="google.co.in"` to search through Google's Indian domain:

```python
results = client.search(
    engine="google",
    q="best coffee beans",
    google_domain="google.co.in",
    gl="in",
    hl="en",
    location="Mumbai, Maharashtra",
)
```

## Finding Valid Locations

Call `client.locations()` to find location names accepted by SerpApi:

```python
locations = client.locations(q="Mumbai", limit=5)

for location in locations:
    print(location.get("canonical_name"))
```

See [Account and Locations](../user_guide/account-and-locations.md) for details on choosing a location. Use the [SerpApi Playground](https://serpapi.com/playground) to test location values with the rest of your search parameters.
