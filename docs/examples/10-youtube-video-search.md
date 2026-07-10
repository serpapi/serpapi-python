---
title: "YouTube Video Search"
description: "Search YouTube videos and read video result metadata."
---

# YouTube Video Search

Use the YouTube Search API when you need video discovery results, channel references, or topic-level video monitoring. YouTube uses `search_query` instead of `q`.

## Search Videos

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

## What to Read

Start with `video_results`. Useful fields include `title`, `link`, `channel`, `views`, `published_date`, `length`, and `thumbnail`. Some queries return additional sections such as channels, playlists, shorts, or related searches.

See the [YouTube Search API documentation](https://serpapi.com/youtube-search-api) for YouTube-specific parameters. The [SerpApi Playground](https://serpapi.com/playground) is the quickest way to inspect the exact response shape for your query.
