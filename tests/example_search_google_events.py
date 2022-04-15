# test google events
import unittest
import os
import serpapi

class TestGoogleEvents(unittest.TestCase):

  @unittest.skipIf((os.getenv("API_KEY") == None), "no api_key provided")
  def test_search_google_events(self):
    client = serpapi.Client({
        'engine': 'google_events',
        'api_key': os.getenv("API_KEY")
      })
    data = client.search({
        'q': 'coffee', 
    })
    self.assertIsNone(data.get('error'))
    self.assertIsNotNone(data['events_results'])
    # os.getenv("API_KEY") captures the secret user API available from http://serpapi.com
  