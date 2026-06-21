---
title: "Zero Trace and Data Retention"
description: "Use zero_trace, no_cache, and async choices intentionally."
guide-section: "Advanced Usage"
---

# Zero Trace and Data Retention

SerpApi exposes request parameters for data retention and cache behavior. The Python client passes these parameters through to the API.

## Zero Trace

When enabled for your account, pass `zero_trace=true` to request zero data retention behavior for a search:

```python
results = client.search({
    "engine": "google",
    "q": "coffee",
    "location": "Austin, Texas",
    "zero_trace": True,
})
```

Use this for workloads that require stricter data handling. Zero trace availability and behavior are account-dependent, so confirm details in the [SerpApi Search API documentation](https://serpapi.com/search-api) and your plan.

## Cache Controls

Use `no_cache=true` when you want SerpApi to fetch fresh results instead of using cached results:

```python
results = client.search({
    "engine": "google",
    "q": "coffee",
    "no_cache": True,
})
```

`no_cache=true` and `async=true` should not be used together.

## Choosing Between Modes

| Need | Parameter |
| --- | --- |
| Fresh live results | `no_cache=true` |
| Submit now and fetch later | `async=true` plus `search_archive()` |
| Zero data retention behavior | `zero_trace=true` when enabled for your account |

See [Async Search Archive](async-search-archive.md) for async search usage.

