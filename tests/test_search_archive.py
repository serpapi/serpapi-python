import unittest
import os
import serpapi
import pytest

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
      # search unique search identifier
      search_id = data['search_metadata']['id']
      # fetch results from the archive (free of charge)
      data_archive = client.search_archive(search_id)
      self.assertEqual(data_archive['organic_results'][0], data["organic_results"][0])

      # fetch results from the archive again (code coverage)
      object_archive = client.search_archive(search_id, 'object')
      self.assertIsNotNone(object_archive)
      self.assertEqual(object_archive.organic_results[0].title, data["organic_results"][0]["title"])

      with pytest.raises(serpapi.SerpApiException, match=r'Decoder must be json or html'):
        client.search_archive(search_id, 'bad')
