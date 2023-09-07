# Example: yahoo search engine
import pytest
import os
import serpapi

def test_search_yahoo(client):
  data = client.search({
      'engine': 'yahoo',
      'p': 'coffee',
  })
  assert data.get('error') is None
  assert data['organic_results']
