---
title: "Zero Trace and Data Retention"
description: "Control search storage and request fresh results with zero_trace and no_cache."
---

# Zero Trace and Data Retention

Use `zero_trace` to control whether SerpApi stores a search, and `no_cache` to request fresh results. Pass these parameters to a client created as shown in [Client Usage](client-usage.md#create-a-client).

## Zero Trace

If your account supports ZeroTrace, pass `zero_trace=True` to skip storing search parameters, files, and metadata on SerpApi's servers:

```python
results = client.search(
    engine="google",
    q="coffee",
    location="Austin, Texas",
    zero_trace=True,
)
```

Check your plan and the [SerpApi Search API documentation](https://serpapi.com/search-api) for ZeroTrace availability and data retention details.

## Cache Controls

SerpApi can reuse a saved response when the search parameters match a recent request. Pass `no_cache=True` to fetch fresh results:

```python
results = client.search(
    engine="google",
    q="coffee",
    no_cache=True,
)
```

`no_cache=true` and `async=true` should not be used together.

## Choosing Between Modes

| Need | Parameter |
| --- | --- |
| Fetch fresh results | `no_cache=true` |
| Submit now and fetch later | `async=true` plus `search_archive()` |
| Skip storing the search on SerpApi's servers | `zero_trace=true` when enabled for your account |

The table uses API parameter syntax. In Python, write `True` with a capital `T`. See [Async Search Archive](async-search-archive.md) for how to pass the `async` parameter.
