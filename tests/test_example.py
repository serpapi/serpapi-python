# # Unit testing
# import unittest

# # Operating system
# import os

# # regular expression library
# import re

# # safe queue
# import sys
# if (sys.version_info > (3, 0)):
#   from queue import Queue
# else:
#   from Queue import Queue

# # Time utility
# import time

# # Serp API search
# from serpapi import GoogleSearch

# # download file with wget
# #import wget

# class TestExample(unittest.TestCase):

#     def setUp(self):
#         GoogleSearch.SERP_API_KEY = os.getenv("API_KEY","demo")

#     @unittest.skipIf((os.getenv("API_KEY") == None), "no api_key provided")
#     def test_get_json(self):
#         client = GoogleSearch({"q": "Coffee", "engine": "google_scholar"})
#         data = client.get_json()
#         print(data['search_metadata'])
#         search_id = data['search_metadata']['id']
#         # retrieve search from the archive - blocker
#         print(search_id + ": get search from archive")
#         raw_html =  client.get_search_archive(search_id, 'html')
#         # print(search_id + ": status = " + search_archived['search_metadata']['status'])
#         print(raw_html)
#         #print(search_html)

#     @unittest.skipIf((os.getenv("DEBUGAPI_KEY") == None), "no api_key provided")
#     def test_search_google_images(self):
#         client = GoogleSearch({"q": "coffe", "tbm": "isch"})
#         for image_result in client.get_json()['images_results']:
#             try:
#                 link = image_result["original"]
#                 print("link is found: " + link)
#                 # uncomment the line below to down the original image
#                 # wget.download(link, '.')
#             except:
#                 print("link is not found.")
#                 pass
#             # https://github.com/serpapi/showcase-serpapi-tensorflow-keras-image-training/blob/master/fetch.py

#     @unittest.skipIf((os.getenv("DEBUGAPI_KEY") == None), "no api_key provided")
#     def test_async(self):
#         # store searches
#         search_queue = Queue()

#         # Serp API search
#         client = GoogleSearch({
#             "location": "Austin,Texas",
#             "async": True
#         })

#         # loop through companies
#         for company in ['amd','nvidia','intel']:
#           print("execute async search: q = " + company)
#           client.params_dict["q"] = company
#           data = client.get_dict()
#           if data is not None:
#               print("oops data is empty for: " + company)
#               continue
#           print("add search to the queue where id: " + data['search_metadata']['id'])
#           # add search to the search_queue
#           search_queue.put(data)

#         print("wait until all search statuses are cached or success")

#         # Create regular search
#         client = GoogleSearch({"async": True})
#         while not search_queue.empty():
#           data = search_queue.get()
#           search_id = data['search_metadata']['id']

#           # retrieve search from the archive - blocker
#           print(search_id + ": get search from archive")
#           search_archived =  client.get_search_archive(search_id)
#           print(search_id + ": status = " + search_archived['search_metadata']['status'])

#           # check status
#           if re.search('Cached|Success', search_archived['search_metadata']['status']):
#             print(search_id + ": search done with q = " + search_archived['search_parameters']['q'])
#           else:
#             # requeue search_queue
#             print(search_id + ": requeue search")
#             search_queue.put(search)
#             # wait 1s
#             time.sleep(1)
#         # search is over.
#         print('all searches completed')

#     @unittest.skipIf((os.getenv("DEBUGAPI_KEY") == None), "no api_key provided")
#     def test_search_google_news(self):
#         client = GoogleSearch({
#             "q": "coffe",   # search search
#             "tbm": "nws",   # news
#             "tbs": "qdr:d", # last 24h
#             "num": 10
#         })
#         for offset in [0,1,2]:
#             client.params_dict["start"] = offset * 10
#             data = client.get_json()
#             for news_result in data['news_results']:
#                 print(str(news_result['position'] + offset * 10) + " - " + news_result['title'])

#     @unittest.skipIf((os.getenv("DEBUGAPI_KEY") == None), "no api_key provided")
#     def test_search_google_shopping(self):
#         client = GoogleSearch({
#             "q": "coffe",   # search search
#             "tbm": "shop",  # news
#             "tbs": "p_ord:rv", # last 24h
#             "num": 100
#         })
#         data = client.get_json()
#         if 'shopping_results' in data:
#             for shopping_result in data['shopping_results']:
#                 print(str(shopping_result['position']) + " - " + shopping_result['title'])
#         else:
#             print("WARNING: oops shopping_results is missing from search result with tbm=shop")

#     @unittest.skipIf((os.getenv("DEBUGAPI_KEY") == None), "no api_key provided")
#     def test_search_by_location(self):
#         for city in ["new york", "paris", "berlin"]:
#             location = GoogleSearch({}).get_location(city, 1)[0]["canonical_name"]
#             client = GoogleSearch({
#                 "q": "best coffee shop",   # search search
#                 "location": location,
#                 "num": 10,
#                 "start": 0
#             })
#             data = client.get_json()
#             self.assertIsNone(data.get("error"))
#             top_result = data['organic_results'][0]["title"]
#             print("top coffee result for " + location + " is: " + top_result)


# if __name__ == '__main__':
#     unittest.main()
