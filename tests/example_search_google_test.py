# Example: google search engine
import pytest
import os
import serpapi

def test_search_google(client):

  data = client.search({
      'engine': 'google',
      'q': 'coffee',
      'engine': 'google',
  })
  assert data.get('error') is None
  assert data['organic_results']
