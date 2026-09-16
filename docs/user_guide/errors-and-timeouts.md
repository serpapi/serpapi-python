---
title: "Errors and Timeouts"
description: "Handle SerpApi HTTP errors, connection errors, timeouts, and API-level errors."
---

# Errors and Timeouts

The client raises exceptions when a request times out, cannot connect, or receives an HTTP error. Use `try` and `except` to decide what your script should do when a request fails.

The examples use a client created as shown in [Client Usage](client-usage.md#create-a-client).

## HTTP Errors

HTTP responses with a 4xx or 5xx status code raise `serpapi.HTTPError`:

```python
import serpapi

try:
    results = client.search(engine="google", q="coffee")
except serpapi.HTTPError as exc:
    print("Status:", exc.status_code)
    print("Error:", exc.error)
```

`exc.status_code` contains the HTTP status code, such as `401` for an invalid API key. `exc.error` contains the error message from SerpApi's JSON response, or `None` if the response has no JSON error message.

See [SerpApi API status and error codes](https://serpapi.com/api-status-and-error-codes) for the meaning of each status and how to resolve it.

## Connection Errors and Timeouts

Catch `TimeoutError` when a request takes too long to connect or receive data. Catch `HTTPConnectionError` when the client cannot establish a connection:

```python
try:
    results = client.search(engine="google", q="coffee", timeout=10)
except serpapi.TimeoutError:
    print("The request timed out.")
except serpapi.HTTPConnectionError:
    print("Could not connect to SerpApi.")
```

Timeouts are measured in seconds. Set a default for all requests made by a client:

```python
client = serpapi.Client(api_key="secret_api_key", timeout=20)
```

Override it for one request:

```python
results = client.search(
    engine="google",
    q="coffee",
    timeout=5,
)
```

The timeout applies to connecting, reading, writing, and acquiring a pooled connection. Without a timeout setting, the SDK preserves its historical behavior and can wait indefinitely. See the [HTTPX timeout documentation](https://www.python-httpx.org/advanced/timeouts/).

## Missing Search IDs

`search_archive()` requires the ID of a previous search. If you leave out `search_id`, it raises `SearchIDNotProvided`:

```python
try:
    archived = client.search_archive()
except serpapi.SearchIDNotProvided:
    print("Provide search_id from search_metadata.id.")
```

## API-Level Errors in JSON

A response can contain an `error` message even when the HTTP request succeeds. Check for this field before reading the results:

```python
results = client.search(engine="google", q="coffee")

if "error" in results:
    raise RuntimeError(results["error"])
```
