.. serapi-python documentation master file, created by
   sphinx-quickstart on Sun Apr  3 21:09:40 2022.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

**serpapi-python**
==================

an official Python client library for `SerpApi <https://serpapi.com>`_.

--------------

Getting Started
===============

This part of the documentation covers installation of `serpapi-python` and a quick tutorial to get you started.

If you are looking for reference material, please see the :ref:`API Reference <api-reference>`.


Installation
------------

To install ``serpapi-python``, simply use `pip`::

    $ pip install serpapi


Please note that Python 3.6+ is required.

API Reference
=============

.. _api-reference:

This part of the documentation covers all the interfaces of :class:`serpapi` Python module.

.. module:: serpapi
   :platform: Unix, Windows
   :synopsis: SerpApi Python Library

Primary interface
-----------------

The primary interface to `serpapi-python` is through the :class:`serpapi.Client` class.

.. autoclass:: serpapi.Client
   :members:

.. autoclass:: serpapi.client.SerpResults
   :members:



Exceptions
----------

.. autoexception:: serpapi.SerpAPIError
   :members:

.. autoexception:: serpapi.APIKeyNotProvided
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
