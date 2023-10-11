# Example: duckduckgo search engine
import pytest
import os
import serpapi

def test_search_duckduckgo(client):
  data = client.search({
      'engine': 'duckduckgo',
      'q': 'coffee',
  })
  assert data.get('error') is None
  assert data['organic_results']
