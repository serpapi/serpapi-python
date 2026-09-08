---
title: "Migrating from google-search-results"
description: "Move from the deprecated google-search-results SDK to the recommended serpapi package."
---

# Migrating from google-search-results

Both `google-search-results` and `serpapi` use the name `serpapi` in Python imports. Check which package your project installs before updating the code.

## Recommended Package

Use [`serpapi` on PyPI](https://pypi.org/project/serpapi/) for new projects and when updating an existing integration.

Install it with:

```bash
pip install serpapi
```

After [setting your API key](getting-started.md#installation), create a `serpapi.Client`:

```python
import os
import serpapi

YOUR_API_KEY = os.environ["SERPAPI_KEY"]

client = serpapi.Client(api_key=YOUR_API_KEY)
results = client.search(engine="google", q="coffee")

print(results)
```

This is the package used throughout the current documentation.

## Deprecated Package

[`google-search-results` on PyPI](https://pypi.org/project/google-search-results/) is the older Python package. It is deprecated for new integrations.

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

Install only one of these packages in a Python environment. Both provide a `serpapi` module, so installing them together can overwrite files and cause import errors.

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
results = client.search(
    engine="google",
    q="coffee",
    location="Austin, Texas",
)
```

Search parameter names stay the same. You can pass them by name, as in the new example, or keep them in a dictionary and pass that to `client.search()`.

## Migration Checklist

- Remove `google-search-results` from requirements and dependency files.
- Install `serpapi` with `pip install serpapi`.
- Replace `from serpapi import GoogleSearch` with `import serpapi`.
- Replace `GoogleSearch(params).get_dict()` with `serpapi.Client(api_key=...).search(engine=..., q=..., ...)`.
- Keep using the [SerpApi Playground](https://serpapi.com/playground) and the [SerpApi API documentation](https://serpapi.com/search-api) to confirm engine parameters.
