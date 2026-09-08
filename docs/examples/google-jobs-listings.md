---
title: "Google Jobs Listings"
description: "Search job listings by role and location."
---

# Google Jobs Listings

Search Google Jobs for open roles in a location. Results include job titles, employers, and listing sources. You can use them to track hiring or research advertised salaries when salary details are available.

## Search Jobs

[Install the package and set your API key](../user_guide/getting-started.md#installation) before running this example.

```python
import os
import serpapi


client = serpapi.Client(api_key=os.environ["SERPAPI_KEY"], timeout=20)

results = client.search(
    engine="google_jobs",
    q="software engineer",
    location="Austin, Texas",
    hl="en",
    gl="us",
)

for job in results.get("jobs_results", [])[:5]:
    print(job.get("title"))
    print(job.get("company_name"), "-", job.get("location"))
    print(job.get("via"))
```

## Read the Results

Read job listings from `jobs_results`. Typical fields include `title`, `company_name`, `location`, `via`, `description`, `detected_extensions`, and `related_links`. Use the returned links and identifiers to find further details about a listing.

See the [Google Jobs API documentation](https://serpapi.com/google-jobs-api) for language, location, and pagination parameters. Use the [SerpApi Playground](https://serpapi.com/playground) to try different roles and locations.
