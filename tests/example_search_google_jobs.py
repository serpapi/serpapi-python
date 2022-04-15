# test google jobs
import unittest
import os
import serpapi

class TestGoogleJobs(unittest.TestCase):

  @unittest.skipIf((os.getenv("API_KEY") == None), "no api_key provided")
  def test_search_google_jobs(self):
    client = serpapi.Client({
        'engine': 'google_jobs',
        'api_key': os.getenv("API_KEY")
      })
    data = client.search({
        'q': 'coffee', 
    })
    self.assertIsNone(data.get('error'))
    self.assertIsNotNone(data['jobs_results'])
    # os.getenv("API_KEY") captures the secret user API available from http://serpapi.com
  