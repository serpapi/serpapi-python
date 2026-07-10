---
title: "Async Search Archive"
description: "Submit server-side async searches and retrieve them later from the Search Archive API."
guide-section: "Advanced Usage"
---

# Async Search Archive

SerpApi supports server-side async searches. This is different from Python `asyncio`: you submit a search with `async=true`, receive a search ID, and retrieve the completed search later with the Search Archive API.

## Submit an Async Search

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

If the search is still queued or processing, wait and call `search_archive()` again:

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

Async searches are useful when you want to submit work quickly and collect results later, especially from job queues, scheduled workers, or data pipelines.

Do not combine `async=true` with `no_cache=true`. Use the [SerpApi Search Archive API documentation](https://serpapi.com/search-archive-api) for retention windows and status details.
