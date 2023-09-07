# Example: naver search engine
import pytest
import os
import serpapi

def test_search_naver(client):
  data = client.search({
      'engine': 'naver',
      'query': 'coffee',
  })
  assert data.get('error') is None
  assert data['ads_results']
