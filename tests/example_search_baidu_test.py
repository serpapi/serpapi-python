# Example: baidu search engine
import pytest
import os
import serpapi


def test_search_baidu(client):
  data = client.search({
      'engine': 'baidu',
      'q': 'coffee',
  })
  assert data.get('error') is None
  assert data['organic_results']
