---
title: "Errors and Timeouts"
description: "Handle SerpApi HTTP errors, connection errors, timeouts, and API-level errors."
guide-section: "User Guide"
---

# Errors and Timeouts

SerpApi Python wraps common failure modes in package-specific exceptions while preserving useful details from `requests`.

## HTTP Errors

Non-200 responses raise `serpapi.HTTPError`:

```python
import serpapi

try:
    results = client.search(engine="google", q="coffee")
except serpapi.HTTPError as exc:
    print("Status:", exc.status_code)
    print("Error:", exc.error)
```

`exc.status_code` contains the HTTP status code when available. `exc.error` contains the `error` field from SerpApi's JSON response when available.

See [SerpApi API status and error codes](https://serpapi.com/api-status-and-error-codes) for status guidance.

## Connection Errors and Timeouts

```python
try:
    results = client.search(engine="google", q="coffee", timeout=10)
except serpapi.TimeoutError:
    print("The request timed out.")
except serpapi.HTTPConnectionError:
    print("Could not connect to SerpApi.")
```

Set a default timeout on the client:

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

## Missing Search IDs

`search_archive()` requires a `search_id`:

```python
try:
    archived = client.search_archive()
except serpapi.SearchIDNotProvided:
    print("Provide search_id from search_metadata.id.")
```

## API-Level Errors in JSON

Some API responses may include an `error` field in JSON. If your workflow continues after a response is returned, check for that field before using result arrays:

```python
results = client.search(engine="google", q="coffee")

if "error" in results:
    raise RuntimeError(results["error"])
```
