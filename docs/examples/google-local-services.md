---
title: "Google Local Services"
description: "Read Google Local Services advertisements for a service category."
---

# Google Local Services

Search Google Local Services for advertisements from local providers, such as electricians. Results include ratings and phone numbers when available. Use the Google Maps API for general place listings.

## Search Local Services

[Install the package and set your API key](../user_guide/getting-started.md#installation) before running this example.

```python
import os
import serpapi


client = serpapi.Client(api_key=os.environ["SERPAPI_KEY"], timeout=20)

results = client.search(
    engine="google_local_services",
    q="electrician",
    data_cid="6745062158417646970",
)

for ad in results.get("local_ads", [])[:5]:
    print(ad.get("title"))
    print(ad.get("rating"), ad.get("reviews"))
    print(ad.get("phone"))
```

## Read the Results

Read the advertisements from `local_ads`. Useful fields include `title`, `rating`, `reviews`, `phone`, `service_area`, `years_in_business`, and `link` when present.

See the [Google Local Services API documentation](https://serpapi.com/google-local-services-api) for query and provider detail options.
