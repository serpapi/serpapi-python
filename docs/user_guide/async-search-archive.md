---
title: "Async Search Archive"
description: "Submit searches now and retrieve their results later with the Search Archive API."
---

# Async Search Archive

An asynchronous search lets you submit a request now and collect the results later. Set the API's `async` parameter to `true` to receive a search ID, then use that ID with the Search Archive API. Each Python client call still waits for an HTTP response. These methods do not use Python's `asyncio` or `await`.

Create a client as shown in [Client Usage](client-usage.md#create-a-client) before running the examples.

## Submit an Async Search

`async` is a reserved word in Python. Put it in a dictionary and use `**` to pass that dictionary's entries as keyword arguments:

```python
submitted = client.search(
    engine="google",
    q="coffee",
    location="Austin, Texas",
    **{"async": True},
)

search_id = submitted["search_metadata"]["id"]
print(search_id)
```

## Retrieve the Search

```python
archived = client.search_archive(search_id=search_id)

status = archived.get("search_metadata", {}).get("status")
print(status)
```

Check the status before reading the results. If the search is still processing, wait and call `search_archive()` again. This loop checks every two seconds until the search succeeds or reports an error:

```python
import time

while True:
    archived = client.search_archive(search_id=search_id)
    status = archived.get("search_metadata", {}).get("status")

    if status == "Success":
        break

    if status == "Error":
        raise RuntimeError(archived.get("error", "Search failed"))

    time.sleep(2)
```

## When to Use Async Searches

Use asynchronous searches when one part of your program submits searches and another collects the results later. For example, a scheduled job could submit a batch of searches for another worker to process.

Do not combine `async=true` with `no_cache=true`. See the [SerpApi Search Archive API documentation](https://serpapi.com/search-archive-api) for search statuses and how long saved searches remain available.
