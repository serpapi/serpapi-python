import unittest
import os
import pprint
import serpapi
import pytest

# This test shows how to extends serpapi.Client
#  without using client engine wrapper.
# 
class TestSerpApi(unittest.TestCase):

		@unittest.skipIf((os.getenv("API_KEY") == None), "no api_key provided")
		def test_search(self):
			client = serpapi.Client({
				"engine": "google",
				"api_key": os.getenv("API_KEY")
				})
			data = client.search({
        "q": "Coffee", 
				"location": "Austin,Texas" 
      })
			assert data.get("error") == None
			self.assertIsNotNone(data["organic_results"][0]["title"])

		@unittest.skipIf((os.getenv("API_KEY") == None), "no api_key provided")
		def test_html(self):
			client = serpapi.Client({
				"engine": "google",
				"api_key": os.getenv("API_KEY")
				})
			data = client.html({
        "q": "Coffee", 
				"location": "Austin,Texas", 
      })
			self.assertRegex(data, r'</html>$')

		# test ObjectDecoder
		@unittest.skipIf((os.getenv("API_KEY") == None), "no api_key provided")
		def test_object(self):
			client = serpapi.Client({
				"engine": "google",
				"api_key": os.getenv("API_KEY")
				})
			data = client.search({
        "q": "Coffee", 
				"location": "Austin,Texas"
      }, decoder="object")
			self.assertIsInstance(data, object)
			self.assertIsNotNone(data.organic_results)
			self.assertIsInstance(data.organic_results, list)
			self.assertGreater(len(data.organic_results), 3)
			self.assertIsInstance(data.organic_results[0].link, str)

		def test_invalid_api_key(self):
			client = serpapi.Client({
				"engine": "google",
				"api_key": "invalid_api_key"
			})
			with pytest.raises(serpapi.SerpApiException, match=r'Invalid API key'):
				client.search({
					"q": "Coffee", 
					"location": "USA", 
				})

    # TODO file a ticket default search engine is google
		def test_error_missing_engine(self):
			client = serpapi.Client({
				"api_key": os.getenv("API_KEY"),
				"engine": ""
			})
			with pytest.raises(serpapi.SerpApiException, match=r'Unsupported.*search engine.'):
				client.search({"q": "Coffee"})

		def test_missing_q(self):
			client = serpapi.Client({
				"api_key": os.getenv("API_KEY")
			})
			with pytest.raises(serpapi.SerpApiException, match=r'Missing query'):
				client.search({"engine": "google"})

		def debug(self, payload):
			pp = pprint.PrettyPrinter(indent=2)
			pp.pprint(payload)

if __name__ == '__main__':
		unittest.main()
