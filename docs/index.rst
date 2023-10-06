.. serpapi-python documentation master file, created by
   sphinx-quickstart on Sun Apr  3 21:09:40 2022.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

**serpapi-python**
==================

an official Python client library for `SerpApi <https://serpapi.com>`_.

--------------

Installation
------------

To install ``serpapi-python``, simply use `pip`::

    $ pip install serpapi


Please note that Python 3.6+ is required.


Usage
-----

Usage of this module is fairly straight-forward. In general, this module attempts to be as close to the actual API as possible, while still being Pythonic.

For example, the API endpoint ``https://serpapi.com/search.json`` is represented by the method ``serpapi.search()``.

.. code-block:: python

   >>> import serpapi
   >>> s = serpapi.search(q="Coffee", engine="google", location="Austin, Texas", hl="en", gl="us")
   >>> s["organic_results"][0]["link"]
   'https://en.wikipedia.org/wiki/Coffee'

Any parameters that you pass to ``search()`` will be passed to the API. This includes the ``api_key`` parameter, which is required for all requests.

.. _using-api-client-directly:

Using the API Client directly
^^^^^^^^^

To make this less repetitive, and gain the benefit of connection pooling, let's start using the API Client directly::

   >>> client = serpapi.Client(api_key="secret_api_key")
   >>> s = client.search(q="Coffee", engine="google", location="Austin, Texas", hl="en", gl="us")

The ``api_key`` parameter is now automatically passed to all requests made by the client.


Concise Tutorial
----------------

Let's start by searching for ``Coffee`` on Google::

   >>> import serpapi
   >>> s = serpapi.search(q="Coffee", engine="google", location="Austin, Texas", hl="en", gl="us")

The ``s`` variable now contains a :class:`SerpResults <serpapi.SerpResults>` object, which acts just like a standard dictionary, with some convenient functions added on top.

Let's print the first result::

   >>> print(s["organic_results"][0]["link"])
   https://en.wikipedia.org/wiki/Coffee

Let's print the title of the first result, but in a more Pythonic way::

   >>> print(s["organic_results"][0].get("title"))
   Coffee - Wikipedia

The `SerpApi.com API Documentation <https://serpapi.com/search-api>`_ contains a list of all the possible parameters that can be passed to the API.


API Reference
-------------

.. _api-reference:

This part of the documentation covers all the interfaces of :class:`serpapi` Python module.

.. module:: serpapi
   :platform: Unix, Windows
   :synopsis: SerpApi Python Library

.. autofunction:: serpapi.search
.. autofunction:: serpapi.search_archive
.. autofunction:: serpapi.locations
.. autofunction:: serpapi.account



Results from SerpApi.com
------------------------

When a successful search has been executed, the method returns
a :class:`SerpResults <serpapi.SerpResults>` object, which acts just like a standard dictionary,
with some convenient functions added on top.


.. code-block:: python

   >>> s = serpapi.search(q="Coffee", engine="google", location="Austin, Texas", hl="en", gl="us")
   >>> type(s)
   <class 'serpapi.models.SerpResults'>

   >>> s["organic_results"][0]["link"]
   'https://en.wikipedia.org/wiki/Coffee'

   >>> s["search_metadata"]
   {'id': '64c148d35119a60ab1e00cc9', 'status': 'Success', 'json_endpoint': 'https://serpapi.com/searches/a15e1b92727f292c/64c148d35119a60ab1e00cc9.json', 'created_at': '2023-07-26 16:24:51 UTC', 'processed_at': '2023-07-26 16:24:51 UTC', 'google_url': 'https://www.google.com/search?q=Coffee&oq=Coffee&uule=w+CAIQICIdQXVzdGluLFRYLFRleGFzLFVuaXRlZCBTdGF0ZXM&hl=en&gl=us&sourceid=chrome&ie=UTF-8', 'raw_html_file': 'https://serpapi.com/searches/a15e1b92727f292c/64c148d35119a60ab1e00cc9.html', 'total_time_taken': 1.55}

Optionally, if you want exactly a dictionary of the entire response, you can use the ``as_dict()`` method::

   >>> type(s.as_dict())
   <class 'dict'>

You can get the next page of results::

   >>> type(s.next_page())
   <class 'serpapi.models.SerpResults'>

To iterate over all pages of results, it's recommended to :ref:`use the API Client directly <using-api-client-directly>`::

   >>> client = serpapi.Client(api_key="secret_api_key")
   >>> search = client.search(q="Coffee", engine="google", location="Austin, Texas", hl="en", gl="us")
   >>> for page in search.yield_pages():
   ...     print(page["search_metadata"]["page_number"])
   1
   2
   3
   4
   5
   6
   7
   8
   9
   10


Here's documentation of the class itself and its methods:

.. autoclass:: serpapi.SerpResults

   .. automethod:: SerpResults.next_page
   .. automethod:: SerpResults.yield_pages
   .. autoproperty:: SerpResults.next_page_url


API Client
----------

The primary interface to `serpapi-python` is through the :class:`serpapi.Client` class.
The primary benefit of using this class is to benefit from Requests' HTTP Connection Pooling.
This class also alleviates the need to pass an ``api_key```  along with every search made to the platform.

.. autoclass:: serpapi.Client

   .. automethod:: Client.search
   .. automethod:: Client.search_archive
   .. automethod:: Client.account
   .. automethod:: Client.locations



Exceptions
----------

.. autoexception:: serpapi.SerpApiError
   :members:

.. autoexception:: serpapi.SearchIDNotProvided
   :members:

.. autoexception:: serpapi.HTTPError
   :members:

.. autoexception:: serpapi.HTTPConnectionError
   :members:





Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
