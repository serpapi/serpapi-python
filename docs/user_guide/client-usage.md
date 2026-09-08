---
title: "Client Usage"
description: "Use the SerpApi client, module helpers, request options, and response helpers."
---

# Client Usage

Create a `serpapi.Client` to reuse your API key, timeout, and HTTP connection settings across requests.

## Create a Client

First, [install the package and set `SERPAPI_KEY`](getting-started.md#installation). The examples on this page use the following client:

```python
import os
import serpapi

client = serpapi.Client(
    api_key=os.environ["SERPAPI_KEY"],
    timeout=20,
)
```

`timeout=20` sets the default connection and read timeout in seconds for this client's requests. It applies to searches, archive lookups, account and location requests, and image uploads. See [Errors and Timeouts](errors-and-timeouts.md#connection-errors-and-timeouts) for how the timeout works.

## Search

Pass search parameters by name, using Python keyword arguments:

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

You can combine a dictionary with keyword arguments. The client adds the keyword arguments to the dictionary and replaces existing values with the same name:

```python
params = {"engine": "google", "q": "coffee"}
results = client.search(params, location="Austin, Texas")
```

## Module Helpers

You can call functions such as `serpapi.search()` directly without creating a client:

```python
import serpapi

results = serpapi.search(
    api_key="secret_api_key",
    engine="google",
    q="coffee",
)
```

These functions use a shared client. Create your own `serpapi.Client` when you need separate settings for an application, test, or worker that runs searches.

## Search Archive

Use `search_archive()` to retrieve a saved search. Get its ID from the original response:

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

`account()` returns account information for your API key. `locations()` returns supported Google locations that match the query. See [Account and Locations](account-and-locations.md) for examples and how to use a location in a search.

## Request Options

`search()`, `search_archive()`, `account()`, and `locations()` pass these keyword arguments to the underlying `requests` call:

| Option | Use |
| --- | --- |
| `timeout` | Set a different timeout, in seconds, for one request. |
| `proxies` | Send the request through a proxy. |
| `verify` | Check the server's TLS certificate, or use a custom certificate authority bundle. |
| `stream` | Set the `requests` streaming option. The client still reads the response before returning results. |
| `cert` | Authenticate the request with a client certificate. |

For example, set a shorter timeout for this search:

```python
results = client.search(
    engine="google",
    q="coffee",
    timeout=10,
)
```

See [Request Options](request-options.md) for proxy, TLS, certificate, and per-request timeout examples.

## Response Objects

For JSON searches, the client returns a `serpapi.SerpResults` object. Read its fields like a dictionary:

```python
first = results["organic_results"][0]
print(first.get("title"))
print(first.get("link"))
```

Use `as_dict()` when another library needs a plain dictionary:

```python
payload = results.as_dict()
```

Use `output="html"` to receive the original search results page as an HTML string:

```python
html = client.search(engine="google", q="coffee", output="html")
print(html[:500])
```

Use `output="md"` to receive a Markdown string, for example to pass search results to an AI agent:

```python
markdown = client.search(engine="google", q="coffee", output="md")
print(markdown[:500])
```

See [Output Formats](output-formats.md) for details on JSON, Markdown, and HTML responses.

## Pagination Helpers

For one additional page, call `next_page()`:

```python
next_results = results.next_page()
```

Use `yield_pages()` in a loop to read the current page and fetch more pages. This example stops after ten pages, or earlier if there is no next page:

```python
for page_number, page in enumerate(results.yield_pages(max_pages=10), start=1):
    current = page.get("serpapi_pagination", {}).get("current", page_number)
    print(current)
```

See [Pagination](pagination.md) for more examples and how to use Google's `start` parameter.

## Error Handling

Use `try` and `except` to handle a timeout, a connection failure, or an HTTP error:

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

See [Errors and Timeouts](errors-and-timeouts.md) for error details and timeout settings.
