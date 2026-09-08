---
title: "Parameters and Engines"
description: "Choose a search engine and pass its parameters to the Python client."
---

# Parameters and Engines

The `engine` parameter selects which search service to use. The Python client sends your parameters to SerpApi without checking them against a fixed list. You can use a new engine or parameter as soon as SerpApi supports it.

## Full Engine and Parameter Reference

Find the parameters for your search in these resources:

- [SerpApi Search API documentation](https://serpapi.com/search-api) lists supported engines and engine-specific parameters.
- [SerpApi Playground](https://serpapi.com/playground) lets you test a search and copy the exact parameters into Python.
- [Account and Locations](account-and-locations.md) shows how to find valid `location` values from Python.

The Search API docs include engines such as Google Search, Google Maps, Google Images, Google Shopping, Google Scholar, Google Jobs, Bing, DuckDuckGo, Yahoo, Yandex, Baidu, YouTube, eBay, Walmart, Naver, Apple App Store, Home Depot, and many more. Check the docs for the current full list.

## Passing Parameters

Create a client as shown in [Client Usage](client-usage.md#create-a-client). Pass parameters by name, using Python keyword arguments:

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
| `q` | Text to search for. |
| `location` | Geographic location for the search. |
| `google_domain` | Google domain, such as `google.com` or `google.co.in`. |
| `gl` | Country code for the search. |
| `hl` | Interface language. |
| `start` | Number of results to skip when fetching another page. |
| `device` | Device type, such as desktop or mobile. |
| `output` | Response format: `json` (default), `html`, or `md`. |
| `async` | Submit a search now and retrieve its results later. |
| `no_cache` | Force SerpApi to fetch fresh results. |
| `zero_trace` | Skip storing the search on SerpApi's servers when your account supports ZeroTrace. |
| `json_restrictor` | Return only selected JSON fields from the API response. |

For the full supported list and the exact meaning of each parameter, use the [SerpApi Search API documentation](https://serpapi.com/search-api).

See [Output Formats](output-formats.md) for examples of each response format and its Python return type.

## Engine-Specific Names

Different engines use different query parameter names. For example:

```python
google = client.search(engine="google", q="coffee")
ebay = client.search(engine="ebay", _nkw="coffee grinder")
youtube = client.search(engine="youtube", search_query="coffee brewing")
walmart = client.search(engine="walmart", query="coffee")
```

Select the engine in the [SerpApi Playground](https://serpapi.com/playground), try your search, and copy the generated parameters.
