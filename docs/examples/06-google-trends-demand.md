---
title: "Google Trends Demand"
description: "Measure search interest over time with Google Trends."
---

# Google Trends Demand

Use the Google Trends API to compare demand, seasonality, and regional interest. This is useful for content planning, product research, launch timing, and market comparisons.

## Interest Over Time

```python
import os
import serpapi


client = serpapi.Client(api_key=os.environ["SERPAPI_KEY"], timeout=20)

results = client.search(
    engine="google_trends",
    q="electric bikes",
    date="today 12-m",
    geo="US",
    data_type="TIMESERIES",
    tz="420",
)

timeline = results.get("interest_over_time", {}).get("timeline_data", [])

for point in timeline[-5:]:
    value = point.get("values", [{}])[0].get("extracted_value")
    print(point.get("date"), value)
```

## What to Read

For time-series charts, read `interest_over_time.timeline_data`. For regional demand, switch `data_type` to `GEO_MAP_0`. For related terms, use `RELATED_QUERIES` or `RELATED_TOPICS`.

See the [Google Trends API documentation](https://serpapi.com/google-trends-api) for `data_type`, `geo`, `date`, and `tz` options. The [SerpApi Playground](https://serpapi.com/playground) helps confirm that a trend query returns the chart you expect.
