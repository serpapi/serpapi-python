---
title: "Migrating from google-search-results"
description: "Move from the deprecated google-search-results SDK to the recommended serpapi package."
guide-section: "Migration"
---

SerpApi has two Python libraries that use similar import names. For new projects and active integrations, use the recommended `serpapi` package.

## Recommended Package

The new and recommended client is [`serpapi` on PyPI](https://pypi.org/project/serpapi/).

Install it with:

```bash
pip install serpapi
```

Use `serpapi.Client`:

```python
import os
import serpapi

YOUR_API_KEY = os.environ["SERPAPI_KEY"]

client = serpapi.Client(api_key=YOUR_API_KEY)
results = client.search({
    "engine": "google",
    "q": "coffee",
})

print(results)
```

This is the package used throughout the current documentation.

## Deprecated Package

The old Python SDK is [`google-search-results` on PyPI](https://pypi.org/project/google-search-results/). It is deprecated for new integrations.

It was installed with:

```bash
pip install google-search-results
```

Older code often looks like this:

<!-- docs-test: skip deprecated google-search-results package is intentionally not installed here -->
```python
from serpapi import GoogleSearch

search = GoogleSearch({
    "q": "coffee",
    "location": "Austin,Texas",
    "api_key": "<your secret api key>",
})
result = search.get_dict()
```

Do not add this package to new projects.

## Update Your Dependencies

Remove `google-search-results` from your dependency files, such as `requirements.txt`, `pyproject.toml`, `setup.py`, `Pipfile`, or Poetry dependency configuration.

Then add `serpapi` instead:

```bash
pip install serpapi
```

Avoid installing both packages in the same environment. They can share the `serpapi` import namespace, which makes migration harder to reason about.

## Update Your Code

Replace `GoogleSearch(...).get_dict()` with `serpapi.Client(...).search(...)`.

Old:

<!-- docs-test: skip deprecated google-search-results package is intentionally not installed here -->
```python
from serpapi import GoogleSearch

search = GoogleSearch({
    "q": "coffee",
    "location": "Austin,Texas",
    "api_key": "<your secret api key>",
})
result = search.get_dict()
```

New:

```python
import os
import serpapi

client = serpapi.Client(api_key=os.environ["SERPAPI_KEY"])
results = client.search({
    "engine": "google",
    "q": "coffee",
    "location": "Austin, Texas",
})
```

Search parameters are still passed as a dictionary, so most request parameter usage can move over directly. The main change is the client interface.

## Migration Checklist

- Remove `google-search-results` from requirements and dependency files.
- Install `serpapi` with `pip install serpapi`.
- Replace `from serpapi import GoogleSearch` with `import serpapi`.
- Replace `GoogleSearch(params).get_dict()` with `serpapi.Client(api_key=...).search(params)`.
- Keep using the [SerpApi Playground](https://serpapi.com/playground) and the [SerpApi API documentation](https://serpapi.com/search-api) to confirm engine parameters.
