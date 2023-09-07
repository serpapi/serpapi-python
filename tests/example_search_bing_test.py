# Example: bing search engine
import pytest
import os
import serpapi

def test_search_bing(client):
  data = client.search({
      'engine': 'bing',
      'q': 'coffee',
  })
  assert data.get('error') is None
  assert data['organic_results']
