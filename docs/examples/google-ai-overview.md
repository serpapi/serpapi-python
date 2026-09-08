---
title: "Google AI Overview"
description: "Read a Google AI Overview answer or retrieve it with a page token."
---

# Google AI Overview

Some Google searches include an AI Overview answer. If the response contains `ai_overview.page_token`, use that token in a second request to retrieve the answer. Tokens expire quickly, so make the second request as soon as you receive one.

## Search and Fetch AI Overview

[Install the package and set your API key](../user_guide/getting-started.md#installation) before running this example.

```python
import os
import serpapi


client = serpapi.Client(api_key=os.environ["SERPAPI_KEY"], timeout=20)

search = client.search(
    engine="google",
    q="how do noise cancelling headphones work",
    location="Austin, Texas",
    gl="us",
    hl="en",
)

ai_overview = search.get("ai_overview", {})

if ai_overview.get("page_token"):
    response = client.search(
        engine="google_ai_overview",
        page_token=ai_overview["page_token"],
    )
    ai_overview = response.get("ai_overview", {})

for block in ai_overview.get("text_blocks", [])[:3]:
    print(block.get("snippet") or block.get("text"))
```

## Read the Results

The `ai_overview` object can contain `text_blocks` with the answer and `references` with its cited sources. If the first Google Search response already includes the AI Overview content, you can read it directly without the second request.

See the [Google Search API AI Overview docs](https://serpapi.com/search-api#api-examples-results-for-ai-overview) and the [Google AI Overview API documentation](https://serpapi.com/google-ai-overview-api). Use the [SerpApi Playground](https://serpapi.com/playground) to find queries that currently return AI Overview data.
