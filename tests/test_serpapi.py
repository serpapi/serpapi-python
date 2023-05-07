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

		def test_invalid_decoder(self):
			client = serpapi.Client({
				"engine": "google",
				"api_key": os.getenv("API_KEY")
			})
			mockResponse = MockResponse()
			self.assertEqual(mockResponse.status, 200)
			with pytest.raises(serpapi.SerpApiException, match=r'Invalid decoder'):
				client.decode(mockResponse, 'bad')

		@unittest.skipIf((os.getenv("API_KEY") == None), "no api_key provided")
		def test_error_missing_engine(self):
			client = serpapi.Client({
				"api_key": os.getenv("API_KEY"),
				"engine": ""
			})
			with pytest.raises(serpapi.SerpApiException, match=r'Unsupported.*search engine.'):
				client.search({"q": "Coffee"})

		@unittest.skipIf((os.getenv("API_KEY") == None), "no api_key provided")
		def test_missing_q(self):
			client = serpapi.Client({
				"api_key": os.getenv("API_KEY")
			})
			with pytest.raises(serpapi.SerpApiException, match=r'Missing query'):
				client.search({"engine": "google"})

		@unittest.skipIf((os.getenv("API_KEY") == None), "no api_key provided")
		def test_no_parameter(self):
			client = serpapi.Client()
			with pytest.raises(serpapi.SerpApiException, match=r'Missing query'):
				client.search({"engine": "google", 'api_key': os.getenv('API_KEY')})


		def debug(self, payload):
			pp = pprint.PrettyPrinter(indent=2)
			pp.pprint(payload)

# Mock object to enable higher code coverage
#
class MockResponse:
	'''Mock HTTP response in order to test serpapi.decode'''
	def __init__(self, status=200):
		self.status = 200
		self.data = MockString("{}")

class MockString:
	def __init__(self, data: str):
		self.data = data

	def decode(self, encoding) -> str:
		return self.data 

if __name__ == '__main__':
		unittest.main()
