---
title: "Pagination"
description: "Collect additional pages with SerpResults helpers or engine-specific offsets."
---

# Pagination

Pagination means fetching more than one page of search results. If a JSON response includes a next-page link in `serpapi_pagination`, you can read it with `results.next_page_url` or fetch pages with `next_page()` and `yield_pages()`.

The examples below use a client created as shown in [Client Usage](client-usage.md#create-a-client).

## Fetch One More Page

```python
results = client.search(
    engine="google",
    q="coffee",
    location="Austin, Texas",
)

next_results = results.next_page()

if next_results:
    for item in next_results.get("organic_results", []):
        print(item.get("title"))
```

`next_page()` returns `None` when the response does not include a next page URL.

## Iterate Through Pages

Use `yield_pages()` when you want the current page plus following pages:

```python
results = client.search(
    engine="google",
    q="coffee",
    location="Austin, Texas",
)

for page in results.yield_pages(max_pages=5):
    for item in page.get("organic_results", []):
        print(item.get("position"), item.get("title"))
```

Set `max_pages` to limit how many pages your script reads, including the first page. Each additional page requires another request. The loop stops early if there is no next-page link, and results may change between requests.

## Google `start` Offsets

Google's `start` parameter tells SerpApi how many results to skip. For example, `start=10` skips the first ten results:

```python
for start in [0, 10, 20]:
    page = client.search(
        engine="google",
        q="coffee",
        location="Austin, Texas",
        start=start,
    )

    print("Offset:", start)
    for item in page.get("organic_results", []):
        print(item.get("title"))
```

Set offsets yourself when you need particular result ranges or want to request several ranges at the same time.

## Store Only What You Need

To keep less data in memory or storage, copy the fields you need into a list of dictionaries:

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
