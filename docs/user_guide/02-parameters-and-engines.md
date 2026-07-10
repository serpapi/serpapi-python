---
title: "Parameters and Engines"
description: "How Python parameters map to SerpApi engines and where to find the full supported list."
guide-section: "User Guide"
---

# Parameters and Engines

SerpApi Python forwards search parameters to the SerpApi HTTP API. The package does not keep a separate engine schema, so new engines and engine parameters can be used as soon as they are supported by SerpApi.

## Full Engine and Parameter Reference

Use these SerpApi resources as the source of truth:

- [SerpApi Search API documentation](https://serpapi.com/search-api) lists supported engines and engine-specific parameters.
- [SerpApi Playground](https://serpapi.com/playground) lets you test a search and copy the exact parameters into Python.
- [Account and Locations](account-and-locations.md) shows how to find valid `location` values from Python.

The Search API docs include engines such as Google Search, Google Maps, Google Images, Google Shopping, Google Scholar, Google Jobs, Bing, DuckDuckGo, Yahoo, Yandex, Baidu, YouTube, eBay, Walmart, Naver, Apple App Store, Home Depot, and many more. Check the docs for the current full list.

## Passing Parameters

Pass engine parameters as keyword arguments:

```python
results = client.search(
    engine="google",
    q="coffee",
    location="Austin, Texas",
    hl="en",
    gl="us",
)
```

You can also pass a dictionary when you already have parameters in one:

```python
params = {
    "engine": "google",
    "q": "coffee",
    "location": "Austin, Texas",
    "hl": "en",
    "gl": "us",
}
results = client.search(params)
```

## Common Google Parameters

These are common Google Search parameters. Other engines have their own parameter names.

| Parameter | Purpose |
| --- | --- |
| `engine` | Search engine. Use `google` for Google Search. |
| `q` | Search query. |
| `location` | Geographic location for the search. |
| `google_domain` | Google domain, such as `google.com` or `google.co.in`. |
| `gl` | Country code for the search. |
| `hl` | Interface language. |
| `start` | Result offset for pagination. |
| `device` | Device type, such as desktop or mobile. |
| `output` | Response format, usually `json` or `html`. |
| `async` | Submit a server-side async search. |
| `no_cache` | Force SerpApi to fetch fresh results. |
| `zero_trace` | Request zero data retention behavior when enabled for your account. |
| `json_restrictor` | Return only selected JSON fields from the API response. |

For the full supported list and the exact meaning of each parameter, use the [SerpApi Search API documentation](https://serpapi.com/search-api).

## Engine-Specific Names

Different engines use different query parameter names. For example:

```python
google = client.search(engine="google", q="coffee")
ebay = client.search(engine="ebay", _nkw="coffee grinder")
youtube = client.search(engine="youtube", search_query="coffee brewing")
walmart = client.search(engine="walmart", query="coffee")
```

When in doubt, open the engine in the [SerpApi Playground](https://serpapi.com/playground), set up the search, and copy the generated parameters.
