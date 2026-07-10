---
title: "Tripadvisor Travel Search"
description: "Search Tripadvisor places, hotels, restaurants, and attractions."
---

# Tripadvisor Travel Search

Use the Tripadvisor Search API when you need destination, hotel, restaurant, attraction, or forum search results from Tripadvisor. The `ssrc` parameter narrows the search to a result type such as hotels, restaurants, or things to do.

## Search Places

```python
import os
import serpapi


client = serpapi.Client(api_key=os.environ["SERPAPI_KEY"], timeout=20)

results = client.search(
    engine="tripadvisor",
    q="Rome",
    ssrc="h",
)

for place in results.get("places", [])[:5]:
    print(place.get("title"))
    print(place.get("place_type"), place.get("location"))
    print(place.get("link"))
```

## What to Read

Start with `places`. Useful fields include `title`, `place_type`, `place_id`, `location`, `description`, `thumbnail`, `link`, and `serpapi_link`.

Use `ssrc` to focus the search: `h` for hotels, `r` for restaurants, `A` for things to do, `g` for destinations, and `a` for all results. See the [Tripadvisor Search API documentation](https://serpapi.com/tripadvisor-search-api) for the current filter and pagination options.
