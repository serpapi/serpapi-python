---
title: "Google Flights Travel"
description: "Search round-trip flight options with Google Flights."
---

# Google Flights Travel

Use the Google Flights API for travel search, flight price research, or building itinerary comparison tools. Flight searches are date-sensitive, so use future dates and choose airport codes that match the route you want.

## Search Round-Trip Flights

```python
import os
import serpapi


client = serpapi.Client(api_key=os.environ["SERPAPI_KEY"], timeout=30)

results = client.search(
    engine="google_flights",
    departure_id="AUS",
    arrival_id="LAX",
    outbound_date="2026-09-15",
    return_date="2026-09-22",
    currency="USD",
    hl="en",
    gl="us",
)

flights = results.get("best_flights") or results.get("other_flights", [])

for itinerary in flights[:3]:
    print("Total price:", itinerary.get("price"))
    for flight in itinerary.get("flights", []):
        print(flight.get("departure_airport", {}).get("id"), "->", flight.get("arrival_airport", {}).get("id"))
```

## What to Read

Start with `best_flights`, then fall back to `other_flights` when needed. Useful fields include `price`, `total_duration`, `carbon_emissions`, and the nested `flights` list for airline, airport, and timing data.

For trip type, cabin, date, currency, and airport parameters, see the [Google Flights API documentation](https://serpapi.com/google-flights-api). The [SerpApi Playground](https://serpapi.com/playground) is useful for testing routes before adding them to code.
