---
title: "Google Trends Demand"
description: "Compare search interest over time with Google Trends."
---

# Google Trends Demand

Use Google Trends to compare search interest over time and between regions. You can look for seasonal patterns when planning content, researching products, or choosing a launch date.

## Interest Over Time

[Install the package and set your API key](../user_guide/getting-started.md#installation) before running this example.

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

## Read the Results

Read `interest_over_time.timeline_data` for search interest over time. Set `data_type="GEO_MAP_0"` to compare regions, or use `RELATED_QUERIES` or `RELATED_TOPICS` to find related searches.

See the [Google Trends API documentation](https://serpapi.com/google-trends-api) for `data_type`, `geo`, `date`, and `tz` options. The [SerpApi Playground](https://serpapi.com/playground) helps confirm that a trend query returns the chart you expect.
