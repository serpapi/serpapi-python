"""SerpApi.com client implementation in Python.
This simple HTTP client allow to interact with SerpApi.com

See: https://serpapi.com for more information
"""

from .__version__ import __version__
from .exceptions import SerpApiException
from .core import Client

__author__ = "serpapi.com"
__license__ = "MIT"
