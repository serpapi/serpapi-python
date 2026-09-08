---
title: "Google Images Search"
description: "Search Google Images and read image titles, sources, and URLs."
---

# Google Images Search

Search Google Images for thumbnails, source pages, and links to the original images.

## Search Images

[Install the package and set your API key](../user_guide/getting-started.md#installation) before running this example.

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

## Read the Results

Read the images from `images_results`. Useful fields include `title`, `source`, `link`, `thumbnail`, `original`, `original_width`, and `original_height`.

See the [Google Images API documentation](https://serpapi.com/google-images-api) for image filters and pagination.
