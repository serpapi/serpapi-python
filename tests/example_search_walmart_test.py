# Example: walmart search engine
import pytest
import os
import serpapi

def test_search_walmart(client):
  data = client.search({
      'engine': 'walmart',
      'query': 'coffee',
  })
  assert data.get('error') is None
  assert data['organic_results']

