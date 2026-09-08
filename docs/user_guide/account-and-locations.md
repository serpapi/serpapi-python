---
title: "Account and Locations"
description: "Check your search allowance and find locations for Google searches."
---

# Account and Locations

Use `client.account()` to check your account and `client.locations()` to find locations for a Google search.

## Account

After [setting your API key](getting-started.md#installation), call `account()` to read your account information:

```python
import os
import serpapi

client = serpapi.Client(api_key=os.environ["SERPAPI_KEY"])

account = client.account()
print(account)
```

The returned dictionary includes `total_searches_left`, `this_month_usage`, and `account_rate_limit_per_hour`. You can check these before running a batch of searches. See the [Account API documentation](https://serpapi.com/account-api) for all fields.

## Locations

Use `locations()` to find supported Google locations:

```python
locations = client.locations(q="Austin", limit=5)

for location in locations:
    print(location.get("name"), location.get("canonical_name"))
```

Choose a `canonical_name` from the returned locations and pass it to a search. For example:

```python
results = client.search(
    engine="google",
    q="coffee",
    location="Austin, Texas, United States",
)
```

See the [SerpApi Locations API documentation](https://serpapi.com/locations-api) for supported parameters and response fields.
