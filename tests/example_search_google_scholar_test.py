# Example: google_scholar search engine
import pytest
import os
import serpapi

def test_search_google_scholar(client):

  data = client.search({
      'engine': 'google_scholar',
      'q': 'coffee',
  })
  assert data.get('error') is None
  assert data['organic_results']
