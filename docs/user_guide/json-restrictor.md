---
title: "JSON Restrictor"
description: "Request selected JSON fields with json_restrictor."
---

# JSON Restrictor

Use `json_restrictor` to ask SerpApi to return selected fields. For example, you can request titles and links while leaving out images and other sections you do not need. SerpApi filters the response before sending it to your program.

The parameter works across SerpApi engines. Its value is a selector string that names the fields to keep. See the [SerpApi JSON Restrictor documentation](https://serpapi.com/json-restrictor) for all selector operators.

Create a client as shown in [Client Usage](client-usage.md#create-a-client) before running the examples.

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

Use `[]` to select every item in a JSON array, which becomes a list in Python. List field names inside `.{...}` to keep several fields from each item:

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

The response keeps the `organic_results` list. Each result in that list contains only the selected fields that are present.

## Select One Item or a Slice

Use `[0]` to select the first item in a list. As in Python, indexes start at zero:

```python
results = client.search(
    engine="google",
    q="coffee",
    json_restrictor="organic_results[0]",
)

first_result = results["organic_results"][0]
print(first_result["title"])
```

Use a slice to select a range of items. The start index is included and the end index is excluded:

```python
results = client.search(
    engine="google",
    q="coffee",
    json_restrictor="organic_results[0:3]",
)
```

`organic_results[0:3]` keeps indexes `0`, `1`, and `2`, so it returns at most three items.

## Combine Multiple Selectors

Separate selectors with commas to keep more than one part of the response:

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

Use dots to select fields inside other fields. This selector keeps each result's title and the links in its `sitelinks.inline` list:

```python
results = client.search(
    engine="google",
    q="coffee",
    json_restrictor="organic_results[].{title, sitelinks.inline[].link}",
)
```

The selected links remain inside `sitelinks.inline`, so your code can read them at the same location as in the full response.

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

- First make a search without `json_restrictor` and inspect the response. Then add selectors for the fields you need.
- Check selectors against a response from the engine you are using. Result sections and field names vary between engines.
- If you plan to call `next_page()` or `yield_pages()`, include `serpapi_pagination` in the selector so the client can find the next-page URL.
- If you need a search ID, status, or archive metadata, include `search_metadata`.

To fetch more pages, keep `serpapi_pagination` alongside the result fields:

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
