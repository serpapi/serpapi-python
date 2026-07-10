---
title: "Google Local Services"
description: "Read Google Local Services ad cards for a service category."
---

# Google Local Services

Use the Google Local Services API when you need local services ad data for a category, provider, or market. It returns ad cards rather than general Google Maps place results.

## Search Local Services

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

## What to Read

Start with `local_ads`. Useful fields include `title`, `rating`, `reviews`, `phone`, `service_area`, `years_in_business`, and `link` when present.

See the [Google Local Services API documentation](https://serpapi.com/google-local-services-api) for query and provider detail options.
