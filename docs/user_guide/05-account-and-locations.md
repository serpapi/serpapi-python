---
title: "Account and Locations"
description: "Use account and locations helpers for account metadata and valid Google locations."
guide-section: "User Guide"
---

# Account and Locations

The client includes helpers for SerpApi account metadata and Google locations.

## Account

Use `account()` to inspect information for the configured API key:

```python
import os
import serpapi

client = serpapi.Client(api_key=os.environ["SERPAPI_KEY"])

account = client.account()
print(account)
```

This is useful in diagnostics, internal tooling, and setup checks.

## Locations

Use `locations()` to find supported Google locations:

```python
locations = client.locations(q="Austin", limit=5)

for location in locations:
    print(location.get("name"), location.get("canonical_name"))
```

Then pass the selected location to a search:

```python
results = client.search({
    "engine": "google",
    "q": "coffee",
    "location": "Austin, Texas, United States",
})
```

The [SerpApi Locations API documentation](https://serpapi.com/locations-api) has the full endpoint behavior.

