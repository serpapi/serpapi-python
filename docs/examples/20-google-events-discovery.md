---
title: "Google Events Discovery"
description: "Search Google Events for upcoming event cards."
---

# Google Events Discovery

Use the Google Events API when you need event cards for a topic, venue, or local market. It returns event-specific metadata instead of general organic search results.

## Search Events

```python
import os
import serpapi


client = serpapi.Client(api_key=os.environ["SERPAPI_KEY"], timeout=20)

results = client.search(
    engine="google_events",
    q="coffee",
)

for event in results.get("events_results", [])[:5]:
    print(event.get("title"))
    print(event.get("date", {}).get("when"))
    print(event.get("address"))
```

## What to Read

Start with `events_results`. Useful fields include `title`, `date`, `address`, `link`, `ticket_info`, `venue`, and `description` when present.

See the [Google Events API documentation](https://serpapi.com/google-events-api) for date and location parameters.
