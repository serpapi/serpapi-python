# Example: home_depot search engine
import pytest
import os
import serpapi

def test_search_home_depot(client):

  data = client.search({
      'engine': 'home_depot',
      'q': 'chair',
  })
  assert data.get('error') is None
  assert data['products']
