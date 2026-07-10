---
title: "Google Jobs Listings"
description: "Search job listings by role and location."
---

# Google Jobs Listings

Use the Google Jobs API to collect job cards for a role, market, or hiring workflow. It is useful for market maps, compensation research, and recruiting dashboards.

## Search Jobs

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

## What to Read

Use `jobs_results` for the listing cards. Typical fields include `title`, `company_name`, `location`, `via`, `description`, `detected_extensions`, and `related_links`. For detail pages, check whether the response includes identifiers or links that fit your workflow.

See the [Google Jobs API documentation](https://serpapi.com/google-jobs-api) for localization and pagination parameters. Use the [SerpApi Playground](https://serpapi.com/playground) to test role/location combinations.
