---
title: "Pagination"
description: "Collect additional pages with SerpResults helpers or engine-specific offsets."
guide-section: "User Guide"
---

# Pagination

Many SerpApi responses include pagination metadata. SerpApi Python exposes this through `SerpResults.next_page_url`, `next_page()`, and `yield_pages()`.

## Fetch One More Page

```python
results = client.search({
    "engine": "google",
    "q": "coffee",
    "location": "Austin, Texas",
})

next_results = results.next_page()

if next_results:
    for item in next_results.get("organic_results", []):
        print(item.get("title"))
```

`next_page()` returns `None` when the response does not include a next page URL.

## Iterate Through Pages

Use `yield_pages()` when you want the current page plus following pages:

```python
results = client.search({
    "engine": "google",
    "q": "coffee",
    "location": "Austin, Texas",
})

for page in results.yield_pages(max_pages=5):
    for item in page.get("organic_results", []):
        print(item.get("position"), item.get("title"))
```

Always set `max_pages` deliberately. Search result pages can change over time and some queries expose many pages.

## Google `start` Offsets

Google Search also supports explicit result offsets:

```python
for start in [0, 10, 20]:
    page = client.search({
        "engine": "google",
        "q": "coffee",
        "location": "Austin, Texas",
        "start": start,
    })

    print("Offset:", start)
    for item in page.get("organic_results", []):
        print(item.get("title"))
```

Use this style when you need deterministic offsets or when you want to parallelize independent pages.

## Store Only What You Need

Search responses can be large. For long crawls or scheduled jobs, extract and store only the fields your application needs:

```python
records = []

for page in results.yield_pages(max_pages=3):
    for item in page.get("organic_results", []):
        records.append({
            "title": item.get("title"),
            "link": item.get("link"),
            "snippet": item.get("snippet"),
        })
```

## Pagination Parameters Vary by Engine

`start` is common for Google Search, but other engines may use different pagination parameters. Check the relevant engine page in the [SerpApi Search API documentation](https://serpapi.com/search-api) or build the request in the [SerpApi Playground](https://serpapi.com/playground).

