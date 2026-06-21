---
title: "Google AI Overview"
description: "Read AI Overview data from Google Search results or fetch it with a page token."
---

# Google AI Overview

Google AI Overview data can appear directly inside Google Search results. Sometimes Google requires an extra request using `ai_overview.page_token`; in that case, use the Google AI Overview API immediately because the token expires quickly.

## Search and Fetch AI Overview

```python
import os
import serpapi


client = serpapi.Client(api_key=os.environ["SERPAPI_KEY"], timeout=20)

search = client.search({
    "engine": "google",
    "q": "how do noise cancelling headphones work",
    "location": "Austin, Texas",
    "gl": "us",
    "hl": "en",
})

ai_overview = search.get("ai_overview", {})

if ai_overview.get("page_token"):
    ai_overview = client.search({
        "engine": "google_ai_overview",
        "page_token": ai_overview["page_token"],
    })

for block in ai_overview.get("text_blocks", [])[:3]:
    print(block.get("snippet") or block.get("text"))
```

## What to Read

Use `text_blocks` for the generated answer and `references` for cited sources when present. If the first Google Search response already includes the AI Overview content, you can read it directly without the second request.

See the [Google Search API AI Overview docs](https://serpapi.com/search-api#api-examples-results-for-ai-overview) and the [Google AI Overview API documentation](https://serpapi.com/google-ai-overview-api). Use the [SerpApi Playground](https://serpapi.com/playground) to find queries that currently return AI Overview data.

