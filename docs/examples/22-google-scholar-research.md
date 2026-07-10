---
title: "Google Scholar Research"
description: "Search Google Scholar publications and read citation-focused fields."
---

# Google Scholar Research

Use the Google Scholar API when you need publication search results, citation counts, author links, or research monitoring workflows.

## Search Scholar

```python
import os
import serpapi


client = serpapi.Client(api_key=os.environ["SERPAPI_KEY"], timeout=20)

results = client.search(
    engine="google_scholar",
    q="coffee",
)

for result in results.get("organic_results", [])[:5]:
    print(result.get("title"))
    print(result.get("publication_info", {}).get("summary"))
    print(result.get("inline_links", {}).get("cited_by", {}).get("total"))
```

## What to Read

Start with `organic_results`. Useful fields include `title`, `link`, `publication_info`, `snippet`, `resources`, and `inline_links.cited_by`.

See the [Google Scholar API documentation](https://serpapi.com/google-scholar-api) for author, citation, and date filters.
