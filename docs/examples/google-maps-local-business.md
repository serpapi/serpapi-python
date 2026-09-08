---
title: "Google Maps Local Businesses"
description: "Find local businesses with Google Maps."
---

# Google Maps Local Businesses

Search Google Maps for nearby businesses, for example to build a store locator, find potential customers, or check local search rankings. Set `q` to the business type or name. The `ll` value specifies the map's latitude, longitude, and zoom level.

## Search for Local Businesses

[Install the package and set your API key](../user_guide/getting-started.md#installation) before running this example.

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

## Read the Results

Read business listings from `local_results`. Common fields include `title`, `rating`, `reviews`, `address`, `phone`, `website`, and `gps_coordinates`. Some responses also include `place_results` when the query matches a specific place.

For the complete parameter list, use the [Google Maps API documentation](https://serpapi.com/google-maps-api). Use the [SerpApi Playground](https://serpapi.com/playground) to choose an `ll` value for the area you want to search.
