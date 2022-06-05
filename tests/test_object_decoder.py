import unittest
import os
import pprint
from serpapi.object_decoder import ObjectDecoder
import pytest

class TestObjectDecoder(unittest.TestCase):

  def test_decode_basic(self):
    decoder = ObjectDecoder()
    data = {
      "organic_results": [
        {
          'name': 'ok'
        },
        {
          'name': 'good'
        }
      ]
    }
    obj = decoder.dict2object(data)
    self.assertEqual(len(obj.organic_results), 2)
    self.assertEqual(obj.organic_results[0].name, 'ok')
    self.assertEqual(obj.organic_results[1].name, 'good')

  def test_decode_list(self):
    decoder = ObjectDecoder()
    data = {
      "organic_results": {
          'list': [0,1,2,3,4]
      }
    }
    obj = decoder.dict2object(data)
    print(obj.organic_results.list[0])
    self.assertEqual(len(obj.organic_results.list), 5)
    self.assertEqual(obj.organic_results.list, [0,1,2,3,4])
