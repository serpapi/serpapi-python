from serpapi.client import SerpAPI

serpapi = SerpAPI(
    api_key="26d6d85be7b4dc7706ab9520ddd49dd78a9491a55308c18c4b9f8161ccb00563"
)

params = {"engine": "google", "q": "Coffee", "location": "Austin, Texas, United States"}

search = serpapi.search(params=params)
print(search)
for page in search.yield_pages(max_pages=10):
    print(page)
