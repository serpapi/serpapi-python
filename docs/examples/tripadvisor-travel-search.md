---
title: "Tripadvisor Travel Search"
description: "Search Tripadvisor for destinations, hotels, restaurants, and attractions."
---

# Tripadvisor Travel Search

Search Tripadvisor for destinations, hotels, restaurants, attractions, and forum posts. Set `ssrc` to limit the search to one type of result, such as hotels.

## Search Places

[Install the package and set your API key](../user_guide/getting-started.md#installation) before running this example.

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

## Read the Results

Read the returned places from `places`. Useful fields include `title`, `place_type`, `place_id`, `location`, `description`, `thumbnail`, `link`, and `serpapi_link`.

Choose the result type with `ssrc`: `h` for hotels, `r` for restaurants, `A` for things to do, `g` for destinations, and `a` for all results. See the [Tripadvisor Search API documentation](https://serpapi.com/tripadvisor-search-api) for the current filter and pagination options.
