---
title: "YouTube Video Search"
description: "Search YouTube and read video titles, channels, and links."
---

# YouTube Video Search

Search YouTube for videos about a topic and read their channel details. Set `search_query` to your search text. This engine does not use `q`.

## Search Videos

[Install the package and set your API key](../user_guide/getting-started.md#installation) before running this example.

```python
import os
import serpapi


client = serpapi.Client(api_key=os.environ["SERPAPI_KEY"], timeout=20)

results = client.search(
    engine="youtube",
    search_query="coffee brewing guide",
)

for video in results.get("video_results", [])[:5]:
    print(video.get("title"))
    print(video.get("channel", {}).get("name"))
    print(video.get("link"))
```

## Read the Results

Read videos from `video_results`. Useful fields include `title`, `link`, `channel`, `views`, `published_date`, `length`, and `thumbnail`. Some queries return additional sections such as channels, playlists, shorts, or related searches.

See the [YouTube Search API documentation](https://serpapi.com/youtube-search-api) for YouTube-specific parameters. The [SerpApi Playground](https://serpapi.com/playground) lets you inspect the response fields for your query.
