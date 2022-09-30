# test Google Local Services search engine
import unittest
import os
import serpapi
import urllib3

class TestGoogleLocalServices(unittest.TestCase):

  @unittest.skipIf((os.getenv("API_KEY") == None), "no api_key provided")
  def test_search_google_local_services(self):
    client = serpapi.Client({
        'api_key': os.getenv("API_KEY"),
        'timeout': 61.1,
        'retries': 2
    })

    data = client.search({
        'engine': 'google_local_services',
        'q': 'Electrician', 
        'place_id': 'ChIJOwg_06VPwokRYv534QaPC8g', 
    })
    self.assertIsNone(data.get('error'))
    self.assertIsNotNone(data['local_ads'])
    # os.getenv("API_KEY") captures the secret user API available from http://serpapi.com/manage-api-key
