---
title: "Google Scholar Research"
description: "Search Google Scholar for publications and citation counts."
---

# Google Scholar Research

Search Google Scholar for publications, citation counts, and author links. Repeat a query to check for new research on a topic.

## Search Scholar

[Install the package and set your API key](../user_guide/getting-started.md#installation) before running this example.

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

## Read the Results

Read publications from `organic_results`. Useful fields include `title`, `link`, `publication_info`, `snippet`, `resources`, and `inline_links.cited_by`.

See the [Google Scholar API documentation](https://serpapi.com/google-scholar-api) for author, citation, and date filters.
