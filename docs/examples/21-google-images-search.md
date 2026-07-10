---
title: "Google Images Search"
description: "Search Google Images and read image result metadata."
---

# Google Images Search

Use the Google Images API when you need image discovery results, thumbnails, sources, and original image links.

## Search Images

```python
import os
import serpapi


client = serpapi.Client(api_key=os.environ["SERPAPI_KEY"], timeout=20)

results = client.search(
    engine="google_images",
    tbm="isch",
    q="coffee",
)

for image in results.get("images_results", [])[:5]:
    print(image.get("title"))
    print(image.get("source"))
    print(image.get("original"))
```

## What to Read

Start with `images_results`. Useful fields include `title`, `source`, `link`, `thumbnail`, `original`, `original_width`, and `original_height`.

See the [Google Images API documentation](https://serpapi.com/google-images-api) for image filters and pagination.
