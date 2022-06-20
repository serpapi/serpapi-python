import unittest
import os
import pprint
import serpapi
import pytest

# This test shows how to extends serpapi.Client
#  without using client engine wrapper.
#


class TestSearchArchive(unittest.TestCase):

    @unittest.skipIf((os.getenv("API_KEY") == None), "no api_key provided")
    def test_search_archive(self):
      client = serpapi.Client({
        "engine": "google",
        "api_key": os.getenv("API_KEY")
        })
      data = client.search({
        "q": "Coffee",
        "location": "Austin,Texas"
      })
      self.assertEqual(data.get("error"), None)
      self.assertIsNotNone(data["organic_results"][0]["title"])
      search_id = data['search_metadata']['id']
      data_archive = client.search_archive(search_id)
      self.assertEqual(data_archive['organic_results'][0], data["organic_results"][0])

      # code coverage
      object_archive = client.search_archive(search_id, 'object')
      self.assertIsNotNone(object_archive)
      self.assertEqual(object_archive.organic_results[0].title, data["organic_results"][0]["title"])

      with pytest.raises(serpapi.SerpApiException, match=r'Decoder must be json or html'):
        client.search_archive(search_id, 'bad')
