---
title: "Threading"
description: "Parallelize independent SerpApi requests with ThreadPoolExecutor."
guide-section: "Advanced Usage"
---

# Threading

SerpApi requests are network-bound, so threads are often a simple way to run independent searches concurrently.

## ThreadPoolExecutor Example

```python
import os
import serpapi

from concurrent.futures import ThreadPoolExecutor, as_completed


API_KEY = os.environ["SERPAPI_KEY"]


def search_country(country):
    client = serpapi.Client(api_key=API_KEY, timeout=20)
    results = client.search({
        "engine": "google",
        "q": "best coffee beans",
        "gl": country,
        "hl": "en",
    })
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

- Keep `max_workers` modest and tune it for your quota, latency, and downstream processing.
- Handle exceptions per future so one failed request does not hide all other results.
- Create a client inside each worker when you want clear isolation between threads.
- Use explicit timeouts so blocked network calls do not stall the whole batch.

## Handling Per-Request Errors

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

