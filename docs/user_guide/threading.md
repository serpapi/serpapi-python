---
title: "Threading"
description: "Run several independent searches at the same time with ThreadPoolExecutor."
---

# Threading

Search requests spend time waiting for network responses. Threads let your program make another request while one is waiting. Use them for independent searches, such as running the same query in several countries.

## ThreadPoolExecutor Example

After [setting your API key](getting-started.md#installation), run this example. `max_workers=5` allows up to five searches to run at once. Each submitted task returns a `Future`, an object that holds its eventual result or exception. `as_completed()` gives you each task as it finishes.

```python
import os
import serpapi

from concurrent.futures import ThreadPoolExecutor, as_completed


API_KEY = os.environ["SERPAPI_KEY"]


def search_country(country):
    client = serpapi.Client(api_key=API_KEY, timeout=20)
    results = client.search(
        engine="google",
        q="best coffee beans",
        gl=country,
        hl="en",
    )
    return country, results.get("organic_results", [])


countries = ["us", "gb", "ca", "au", "in"]

with ThreadPoolExecutor(max_workers=5) as executor:
    futures = [executor.submit(search_country, country) for country in countries]

    for future in as_completed(futures):
        country, organic_results = future.result()
        first = organic_results[0] if organic_results else {}
        print(country, first.get("title"))
```

## Practical Guidance

- Start with a small `max_workers` value. Increase it based on your account's search limits, response times, and how quickly your code can process results.
- Handle each task's exception so the loop can continue processing other results.
- Create a client inside each worker to give it a separate HTTP session.
- Set a timeout so a stalled request does not hold up the batch indefinitely.

## Handling Per-Request Errors

`future.result()` raises any exception from the search. Catch it inside the loop to report the failed country and continue:

```python
with ThreadPoolExecutor(max_workers=5) as executor:
    future_to_country = {
        executor.submit(search_country, country): country
        for country in countries
    }

    for future in as_completed(future_to_country):
        country = future_to_country[future]

        try:
            country, organic_results = future.result()
        except serpapi.SerpApiError as exc:
            print("Failed:", country, exc)
            continue

        print("Finished:", country, len(organic_results))
```
