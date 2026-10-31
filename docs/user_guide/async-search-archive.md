---
title: "Async Search Archive"
description: "Submit searches now and retrieve their results later with the Search Archive API."
---

# Async Search Archive

An asynchronous search lets you submit a request now and collect the results later. Set the API's `async` parameter to `true` to receive a search ID, then use that ID with the Search Archive API. Each Python client call still waits for an HTTP response. These methods do not use Python's `asyncio` or `await`.

Create a client as shown in the [client usage guide](client-usage.md#create-a-client) before running the examples.

## Submit an async search

`async` is a reserved word in Python. Put it in a dictionary and use `**` to pass that dictionary's entries as keyword arguments:

```python
submitted = client.search(
    engine="google",
    q="coffee",
    location="Austin, Texas",
    **{"async": True},
    timeout=30,
)

search_id = submitted["search_metadata"]["id"]
print(search_id)
```

## Retrieve the search

```python
archived = client.search_archive(search_id=search_id, timeout=30)

status = archived.get("search_metadata", {}).get("status")
print(status)
```

## Poll for completion

Check the status before reading the results. If the search is still processing, wait and call `search_archive()` again. This example checks every two seconds, with an HTTP timeout of up to 30 seconds per request and a 120-second polling deadline:

```python
import time

deadline = time.monotonic() + 120

while True:
    remaining = deadline - time.monotonic()
    if remaining <= 0:
        raise TimeoutError("Polling timed out before the search completed.")

    archived = client.search_archive(
        search_id=search_id, timeout=min(30, remaining)
    )
    status = archived.get("search_metadata", {}).get("status")

    if status in ("Success", "Cached"):
        break

    if status == "Error":
        raise RuntimeError(archived.get("error", "Search failed"))

    time.sleep(min(2, max(0, deadline - time.monotonic())))
```

The deadline is checked between requests. If the search remains unfinished, the loop raises Python's built-in `TimeoutError`. The HTTP timeout limits connection and read waits for each request; it does not stop repeated successful responses that say the search is still processing.

## When to use async searches

Use asynchronous searches when one part of your program submits searches and another collects the results later. For example, a scheduled job could submit a batch of searches for another worker to process.

Do not combine `async=true` with `no_cache=true`. See the [SerpApi Search Archive API documentation](https://serpapi.com/search-archive-api) for search statuses and how long saved searches remain available.
