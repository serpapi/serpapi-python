---
title: "JSON Restrictor"
description: "Use json_restrictor to request only the JSON fields your workflow needs."
guide-section: "Advanced Usage"
---

# JSON Restrictor

JSON Restrictor is a SerpApi request parameter that limits the JSON response to selected fields before the response is returned to your Python code. Use it for AI workflows, RAG ingestion, reports, and production jobs that only need a narrow subset of a large engine response.

SerpApi supports `json_restrictor` for all engines. The Python client forwards the selector string with the rest of your search parameters. See the [SerpApi JSON Restrictor documentation](https://serpapi.com/json-restrictor) for the full selector reference.

## Select a Top-Level Section

Return only `organic_results`:

```python
results = client.search(
    engine="google",
    q="coffee",
    location="Austin, Texas",
    json_restrictor="organic_results",
)

for result in results.get("organic_results", []):
    print(result.get("title"))
```

## Select Fields From Each Result

Use `[]` to apply a selector to every item in an array. Use a subquery to keep multiple fields from each object:

```python
results = client.search(
    engine="google",
    q="coffee",
    location="Austin, Texas",
    json_restrictor="organic_results[].{title, link, snippet}",
)

for result in results.get("organic_results", []):
    print(result["title"], result["link"])
```

The response still uses the normal SerpApi JSON shape, but each matching result only contains the selected fields.

## Select One Item or a Slice

Use an array index when you only need one item:

```python
results = client.search(
    engine="google",
    q="coffee",
    json_restrictor="organic_results[0]",
)

first_result = results["organic_results"][0]
print(first_result["title"])
```

Use a half-open array slice when you need a fixed number of items:

```python
results = client.search(
    engine="google",
    q="coffee",
    json_restrictor="organic_results[0:3]",
)
```

`organic_results[0:3]` keeps indexes `0`, `1`, and `2`.

## Combine Multiple Selectors

Separate selectors with commas when your workflow needs more than one part of the response:

```python
results = client.search(
    engine="google",
    q="coffee",
    location="Austin, Texas",
    json_restrictor="local_map, organic_results[0]",
)

print(results.get("local_map", {}).get("gps_coordinates"))
print(results["organic_results"][0]["title"])
```

## Nested Fields

Selectors can keep nested values while dropping the surrounding fields you do not use:

```python
results = client.search(
    engine="google",
    q="coffee",
    json_restrictor="organic_results[].{title, sitelinks.inline[].link}",
)
```

This is useful when downstream code only needs a compact list of titles and related links.

## Common Selector Patterns

| Need | `json_restrictor` |
| --- | --- |
| One top-level section | `organic_results` |
| First organic result | `organic_results[0]` |
| First three organic results | `organic_results[0:3]` |
| One field from every result | `organic_results[].title` |
| Multiple fields from every result | `organic_results[].{title, snippet}` |
| Nested fields | `organic_results[].{title, sitelinks.inline[].link}` |
| Multiple response sections | `local_map, organic_results[0]` |

## Practical Guidance

- Start without `json_restrictor`, inspect the response shape, then add selectors for the fields your workflow actually needs.
- Keep selectors close to the engine response you tested. Different engines expose different result sections and field names.
- If you plan to call `next_page()` or `yield_pages()`, include `serpapi_pagination` in the selector so the client can find the next-page URL.
- If you need a search ID, status, or archive metadata, include `search_metadata`.

For paginated collection, keep both the fields you want and the pagination metadata:

```python
results = client.search(
    engine="google",
    q="coffee",
    location="Austin, Texas",
    json_restrictor="organic_results[].{title, link}, serpapi_pagination",
)

for page in results.yield_pages(max_pages=3):
    for result in page.get("organic_results", []):
        print(result["title"], result["link"])
```
