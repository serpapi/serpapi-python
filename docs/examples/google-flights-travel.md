---
title: "Google Flights Travel"
description: "Search for round-trip flights with Google Flights."
---

# Google Flights Travel

Search Google Flights to compare routes, prices, and itineraries. This example searches for a one-week trip starting 30 days from today. `AUS` is Austin and `LAX` is Los Angeles; use the airport codes for your own route.

## Search Round-Trip Flights

[Install the package and set your API key](../user_guide/getting-started.md#installation) before running this example.

```python
import os
import serpapi
from datetime import date, timedelta


client = serpapi.Client(api_key=os.environ["SERPAPI_KEY"], timeout=30)

results = client.search(
    engine="google_flights",
    departure_id="AUS",
    arrival_id="LAX",
    outbound_date=(date.today() + timedelta(days=30)).isoformat(),
    return_date=(date.today() + timedelta(days=37)).isoformat(),
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

## Read the Results

The example reads `best_flights` if it contains results, then tries `other_flights`. Useful fields include `price`, `total_duration`, `carbon_emissions`, and the `flights` list inside each itinerary for airlines, airports, and departure and arrival times.

For trip type, cabin, date, currency, and airport parameters, see the [Google Flights API documentation](https://serpapi.com/google-flights-api). The [SerpApi Playground](https://serpapi.com/playground) lets you test a route before copying the parameters into Python.
