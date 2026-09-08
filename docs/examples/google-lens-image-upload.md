---
title: "Google Lens Image Upload"
description: "Upload a local image to SerpApi and search for visual matches with Google Lens."
---

# Google Lens Image Upload

Search Google Lens with an image on your computer. First upload the file with `client.upload_image()`, then pass the returned `image_id` to `client.search()`.

## Upload and Search

[Install the package and set your API key](../user_guide/getting-started.md#installation) before running this example. Place an image named `image.png` in the directory where you run the script, or replace `image.png` with the path to your file.

Uploads can be JPG/JPEG, PNG, or WebP files up to 500 KB. The returned image ID expires after ten minutes, so search soon after uploading. See the [Image API documentation](https://serpapi.com/image-api) for upload requirements.

```python
import os
import serpapi


client = serpapi.Client(api_key=os.environ["SERPAPI_KEY"], timeout=30)

upload = client.upload_image("image.png")

results = client.search(
    engine="google_lens",
    image_id=upload["image_id"],
    type="visual_matches",
    hl="en",
)

for match in results.get("visual_matches", [])[:5]:
    print(match.get("title"))
    print(match.get("source"))
    print(match.get("link"))
```

`upload_image()` returns a dictionary containing `image_id`. The second call uses that ID to search Google Lens. You can also pass a file opened in binary mode to `upload_image()`. See {py:meth}`serpapi.Client.upload_image` in the API reference.

## Read the Results

Read matching images and pages from `visual_matches`. Each match can include a `title`, `source`, `link`, and `thumbnail`. The example prints up to five matches and prints nothing if that list is empty.

Set `type="products"` to look for products, or `type="exact_matches"` to find pages containing the same image. See the [Google Lens API documentation](https://serpapi.com/google-lens-api) for search types and other parameters.
