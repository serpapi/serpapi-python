---
title: "Google Maps Local Businesses"
description: "Find local businesses with Google Maps results."
---

# Google Maps Local Businesses

Use the Google Maps API for local discovery workflows: store locators, lead generation, local SEO checks, or building a shortlist of nearby places. The most important inputs are the business query and the map coordinate/zoom string in `ll`.

## Search for Local Businesses

```python
import os
import serpapi


client = serpapi.Client(api_key=os.environ["SERPAPI_KEY"], timeout=20)

results = client.search(
    engine="google_maps",
    q="coffee shops",
    ll="@30.2672,-97.7431,14z",
    type="search",
)

for place in results.get("local_results", [])[:5]:
    print(place.get("title"))
    print(place.get("rating"), place.get("reviews"))
    print(place.get("address"))
```

## What to Read

Start with `local_results`. Common fields include `title`, `rating`, `reviews`, `address`, `phone`, `website`, and `gps_coordinates`. Some responses also include `place_results` when the query resolves to a specific place.

For the complete parameter list, use the [Google Maps API documentation](https://serpapi.com/google-maps-api). Use the [SerpApi Playground](https://serpapi.com/playground) to find a working `ll` value for your target market.
