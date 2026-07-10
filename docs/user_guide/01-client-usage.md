---
title: "Client Usage"
description: "Use the SerpApi client, module helpers, request options, and response helpers."
guide-section: "Basics"
---

# Client Usage

The primary interface is `serpapi.Client`. A client keeps the API key, timeout, and HTTP session configuration together, which is useful for applications and scripts that make more than one request.

## Create a Client

```python
import os
import serpapi

client = serpapi.Client(
    api_key=os.environ["SERPAPI_KEY"],
    timeout=20,
)
```

`timeout` becomes the default request timeout for searches, archive lookups, account calls, and locations calls made by this client.

## Search

Pass engine parameters as keyword arguments:

```python
results = client.search(engine="google", q="coffee")
```

You can also pass a dictionary when parameters are already stored in one:

```python
params = {
    "engine": "google",
    "q": "coffee",
}
results = client.search(params)
```

Dictionary parameters and keyword arguments can be mixed. Keyword arguments update the dictionary, which is useful when you start from a saved parameter set:

```python
params = {"engine": "google", "q": "coffee"}
results = client.search(params, location="Austin, Texas")
```

## Module Helpers

For quick scripts, the package exposes module-level helpers:

```python
import serpapi

results = serpapi.search(
    api_key="secret_api_key",
    engine="google",
    q="coffee",
)
```

The helpers use a shared client under the hood. For applications, tests, pagination, and concurrent workloads, prefer creating your own `serpapi.Client`.

## Search Archive

Use `search_archive()` when you have a SerpApi search ID:

```python
search_id = results["search_metadata"]["id"]
archived = client.search_archive(search_id=search_id)
```

If `search_id` is missing, the client raises `serpapi.SearchIDNotProvided`.

## Account and Locations

```python
account = client.account()
locations = client.locations(q="Austin", limit=3)
```

`account()` returns account information for the configured API key. `locations()` returns supported Google locations that match the query; see [Account and Locations](account-and-locations.md) for the local guide and example.

## Request Options

`search()`, `search_archive()`, `account()`, and `locations()` pass these keyword arguments to the underlying `requests` call:

| Option | Use |
| --- | --- |
| `timeout` | Override the client timeout for one request. |
| `proxies` | Send the request through a proxy. |
| `verify` | Control TLS certificate verification. |
| `stream` | Stream the HTTP response. |
| `cert` | Use a client certificate. |

Example:

```python
results = client.search(
    engine="google",
    q="coffee",
    timeout=10,
)
```

See [Request Options](request-options.md) for proxy, TLS, certificate, and per-request timeout examples.

## Response Objects

JSON search responses are returned as `serpapi.SerpResults`. It behaves like a dictionary:

```python
first = results["organic_results"][0]
print(first.get("title"))
print(first.get("link"))
```

Use `as_dict()` when another library needs a plain dictionary:

```python
payload = results.as_dict()
```

If you request `output=html`, the response is plain text instead of `SerpResults`:

```python
html = client.search(engine="google", q="coffee", output="html")
print(html[:500])
```

## Pagination Helpers

For one additional page, call `next_page()`:

```python
next_results = results.next_page()
```

To iterate through all available pages, use `yield_pages()`:

```python
for page in results.yield_pages(max_pages=10):
    print(page["search_metadata"].get("page_number"))
```

See [Pagination](pagination.md) for fuller pagination examples and Google `start` offsets.

## Error Handling

The client raises SerpApi-specific exceptions for common failure modes:

```python
import serpapi

try:
    results = client.search(engine="google", q="coffee")
except serpapi.TimeoutError:
    print("The request timed out.")
except serpapi.HTTPConnectionError:
    print("Could not connect to SerpApi.")
except serpapi.HTTPError as exc:
    print(exc.status_code, exc.error)
```

See [Errors and Timeouts](errors-and-timeouts.md) for status handling guidance.
