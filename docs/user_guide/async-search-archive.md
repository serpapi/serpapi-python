---
title: "Async Search Archive"
description: "Submit searches now and retrieve their results later with the Search Archive API."
---

# Async Search Archive

An asynchronous search lets you submit a request now and collect the results later. Set the API's `async` parameter to `true` to receive a search ID, then use that ID with the Search Archive API. The `async` parameter is separate from Python's `asyncio`. Each `serpapi.Client` call still waits for its HTTP response. To send requests with `asyncio` and `await`, use [`serpapi.AsyncClient`](async-client.md), which also accepts the `async` parameter.

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

## Poll a batch of searches

To run several async searches, submit them all first and keep their search IDs. Then check each unfinished search, set aside the ones that have finished, and check the rest again in the next round. This example submits three searches, then gives them 120 seconds to finish. Each search's parameters are already a dictionary, so `async` goes in it directly:

```python
import time

import serpapi

queries = ["coffee", "tea", "espresso"]

pending = {}
for query in queries:
    params = {
        "engine": "google",
        "q": query,
        "location": "Austin, Texas",
        "async": True,
    }
    submitted = client.search(params, timeout=30)
    pending[submitted["search_metadata"]["id"]] = query

results = {}
failed = {}
deadline = time.monotonic() + 120

while pending:
    for search_id, query in list(pending.items()):
        remaining = deadline - time.monotonic()
        if remaining <= 0:
            raise TimeoutError(f"{len(pending)} searches did not finish.")

        try:
            archived = client.search_archive(
                search_id=search_id, timeout=min(30, remaining)
            )
        except serpapi.HTTPError as exc:
            if exc.status_code not in (500, 503):
                raise
            failed[search_id] = (query, exc.error or "Search failed")
            del pending[search_id]
            continue

        status = archived.get("search_metadata", {}).get("status")

        if status in ("Success", "Cached"):
            results[search_id] = (query, archived)
            del pending[search_id]
        elif status == "Error":
            failed[search_id] = (query, archived.get("error", "Search failed"))
            del pending[search_id]

    if pending:
        time.sleep(min(2, max(0, deadline - time.monotonic())))

for query, archived in results.values():
    count = len(archived.get("organic_results", []))
    print(query, count, archived.get("error", ""))
for query, error in failed.values():
    print(query, "failed:", error)
```

Results are keyed by search ID, so a query that appears twice in the list keeps both results.

In SerpApi's [Status and Error Codes](https://serpapi.com/api-status-and-error-codes) examples, a search with the `Error` status comes back with HTTP 503, which the client raises as `serpapi.HTTPError`. The example moves searches that fail with one of the server errors listed there (500 or 503) to `failed` with their error message, and keeps checking the others. Other errors still stop the loop, such as an invalid API key (401), too many requests or no searches left (429), a connection error, or a request timeout.

A search can also finish with `Success` and still have no results; its `error` field then says why, for example "Google hasn't returned any results for this query."

Pass only `search_id`, and request options such as `timeout`, to `search_archive()`. Don't reuse the parameters from the original search: the Search Archive API rejects `q` with a 400 response, which raises `serpapi.HTTPError`.

## When to use async searches

Use asynchronous searches when one part of your program submits searches and another collects the results later. For example, a scheduled job could submit a batch of searches for another worker to process.

Do not combine `async=true` with `no_cache=true`. See the [SerpApi Search Archive API documentation](https://serpapi.com/search-archive-api) for search statuses and how long saved searches remain available.
