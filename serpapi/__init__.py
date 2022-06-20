"""serpapi.com client implementation in python
This simple HTTP client allow to interact with SerpApi.com

see: https://serpapi.com for more information
"""

from ._version import __version__
from .error import SerpApiException
from .serpapi import Client

__author__ = "Victor Benarbia victor@serpapi.com"
__license__ = "MIT"
