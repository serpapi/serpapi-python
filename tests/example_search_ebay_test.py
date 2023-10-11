# Example: ebay search engine
import pytest
import os
import serpapi

def test_search_ebay(client):
  data = client.search({
      'engine': 'ebay',
      '_nkw': 'coffee',
  })
  assert data.get('error') is None
  assert data['organic_results']
