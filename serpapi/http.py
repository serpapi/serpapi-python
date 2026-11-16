import asyncio
import logging
import os
import re
import ssl

import requests

from .exceptions import (
    HTTPError,
    HTTPConnectionError,
    TimeoutError,
)
from .__version__ import __version__


class HTTPClient:
    """This class handles outgoing HTTP requests to SerpApi.com."""

    BASE_DOMAIN = "https://serpapi.com"
    USER_AGENT = f"serpapi-python, v{__version__}"

    def __init__(self, *, api_key=None, timeout=None):
        # Used to authenticate requests.
        # TODO: do we want to support the environment variable? Seems like a security risk.
        self.api_key = api_key
        self.timeout = timeout
        self.session = requests.Session()

    def request(self, method, path, params, *, assert_200=True, **kwargs):
        # Inject the API Key into the params.
        request_data = kwargs.get("data")
        api_key_in_data = isinstance(request_data, dict) and "api_key" in request_data
        if "api_key" not in params and not api_key_in_data:
            params["api_key"] = self.api_key

        # Build the URL, as needed.
        if not path.startswith("http"):
            url = self.BASE_DOMAIN + path
        else:
            url = path

        # Make the HTTP request.
        try:
            headers = {"User-Agent": self.USER_AGENT}

            # Use the default timeout if one was provided to the client.
            if self.timeout and "timeout" not in kwargs:
                kwargs["timeout"] = self.timeout

            r = self.session.request(
                method=method, url=url, params=params, headers=headers, **kwargs
            )

        except requests.exceptions.ConnectionError as e:
            raise HTTPConnectionError(e)
        except requests.exceptions.Timeout as e:
            raise TimeoutError(e)

        # Raise an exception if the status code is not 200.
        if assert_200:
            try:
                raise_for_status(r)
            except requests.exceptions.HTTPError as e:
                raise HTTPError(e)

        return r


def raise_for_status(r):
    """Raise an exception if the status code is not 200."""
    # TODO: put custom behavior in here for various status codes.

    try:
        r.raise_for_status()
    except requests.exceptions.HTTPError as e:
        raise HTTPError(e)


def _import_httpx2():
    try:
        import httpx2
    except ImportError as e:
        raise ImportError(
            "serpapi.AsyncClient requires Python 3.11 or later and the httpx2 package. "
            'Install the async extra with: pip install "serpapi[async]"'
        ) from e

    return httpx2


class _ApiKeyLogFilter(logging.Filter):
    _API_KEY_IN_URL = re.compile(r"(?i)([?&]api_key=)[^&\s\"']*")

    def filter(self, record):
        message = record.getMessage()
        redacted = self._API_KEY_IN_URL.sub(r"\1<redacted>", message)
        if redacted != message:
            record.msg = redacted
            record.args = ()
        return True


def _protect_httpx2_logs():
    logger = logging.getLogger("httpx2")
    if not any(isinstance(item, _ApiKeyLogFilter) for item in logger.filters):
        logger.addFilter(_ApiKeyLogFilter())


class AsyncHTTPClient:
    """This class handles outgoing asynchronous HTTP requests to SerpApi.com.

    It uses an ``httpx2.AsyncClient`` and accepts the same request options as
    :class:`HTTPClient`, which uses ``requests``.
    """

    BASE_DOMAIN = HTTPClient.BASE_DOMAIN
    USER_AGENT = HTTPClient.USER_AGENT

    # The most HTTP sessions kept open for requests with their own proxies, verify, or cert options.
    _MAX_OPTION_SESSIONS = 16

    def __init__(self, *, api_key=None, timeout=None):
        self._httpx2 = _import_httpx2()
        _protect_httpx2_logs()
        self.api_key = api_key
        self.timeout = timeout
        self._closed = False
        self._close_task = None
        self._option_sessions = {}
        self.session = self._create_session(verify=True)

    async def request(self, method, path, params, *, assert_200=True, **kwargs):
        httpx2 = self._httpx2
        if self._closed:
            raise RuntimeError("Cannot send a request, as the client has been closed.")

        # Inject the API Key into the params.
        request_data = kwargs.get("data")
        api_key_in_data = isinstance(request_data, dict) and "api_key" in request_data
        if "api_key" not in params and not api_key_in_data:
            params["api_key"] = self.api_key

        # Build the URL, as needed.
        if not path.startswith("http"):
            url = self.BASE_DOMAIN + path
        else:
            url = path

        headers = {"User-Agent": self.USER_AGENT}

        # Use the default timeout if one was provided to the client.
        if self.timeout and "timeout" not in kwargs:
            kwargs["timeout"] = self.timeout
        if "timeout" in kwargs:
            kwargs["timeout"] = _httpx2_timeout(httpx2, kwargs["timeout"])

        # Translate the requests options that httpx2 names or handles differently.
        if "allow_redirects" in kwargs:
            kwargs["follow_redirects"] = kwargs.pop("allow_redirects")
        follow_redirects = kwargs.pop("follow_redirects", True)
        # Responses are always read in full, so stream has no effect.
        kwargs.pop("stream", None)
        proxies = kwargs.pop("proxies", None)
        verify = kwargs.pop("verify", None)
        cert = kwargs.pop("cert", None)

        # Encode the URL and body with requests, so they match what HTTPClient sends.
        # httpx2 would replace the query string of a next page URL with the params,
        # and encodes True, False, None, and file uploads differently.
        prepared = requests.PreparedRequest()
        prepared.prepare_method(method)
        prepared.prepare_url(url, params)
        prepared.prepare_headers(None)
        prepared.prepare_body(
            kwargs.pop("data", None) or {},
            kwargs.pop("files", None),
            kwargs.pop("json", None),
        )
        if "Content-Type" in prepared.headers:
            headers["Content-Type"] = prepared.headers["Content-Type"]
        if prepared.body is not None:
            kwargs["content"] = _read_body(prepared.body)

        # Make the HTTP request.
        temporary = False
        try:
            session, temporary = self._session_for(prepared.url, proxies, verify, cert)
            r = await session.request(
                method=method, url=prepared.url, headers=headers,
                follow_redirects=False, **kwargs
            )
            history = []
            while follow_redirects and r.next_request is not None:
                if len(history) >= requests.models.DEFAULT_REDIRECT_LIMIT:
                    raise httpx2.TooManyRedirects(
                        "Exceeded maximum allowed redirects.", request=r.next_request
                    )
                history.append(r)
                next_request = r.next_request
                if temporary:
                    await session.aclose()
                    temporary = False
                # Redirects may change the host or scheme and therefore the selected proxy.
                session, temporary = self._session_for(
                    str(next_request.url), proxies, verify, cert
                )
                r = await session.send(next_request, follow_redirects=False)
                r.history = list(history)
        except httpx2.ConnectTimeout as e:
            # requests reports connection timeouts as connection errors.
            raise _connection_error(e) from e
        except httpx2.TimeoutException as e:
            raise TimeoutError(str(e) or "The request timed out.") from e
        except (
            httpx2.NetworkError, httpx2.ProtocolError, httpx2.ProxyError, ssl.SSLError
        ) as e:
            raise _connection_error(e) from e
        finally:
            if temporary:
                await session.aclose()

        # Raise an exception if the status code is not 200.
        if assert_200 and 400 <= r.status_code < 600:
            raise _status_error(r)

        return r

    async def aclose(self):
        """Close the client's HTTP connections. The client cannot send requests afterwards."""

        self._closed = True
        if self._close_task is None:
            # Close in a task, so that the sessions still close if the caller is cancelled.
            self._close_task = asyncio.create_task(self._close_sessions())
            self._close_task.add_done_callback(self._after_close)

        await asyncio.shield(self._close_task)

    def _after_close(self, close_task):
        self._close_task = None
        # Reading the exception also stops asyncio reporting it as never retrieved.
        if not close_task.cancelled() and close_task.exception() is None:
            self._option_sessions.clear()

    async def _close_sessions(self):
        sessions = [self.session, *self._option_sessions.values()]
        results = await asyncio.gather(
            *(session.aclose() for session in sessions), return_exceptions=True
        )
        for result in results:
            if isinstance(result, asyncio.CancelledError):
                raise result
            if isinstance(result, Exception):
                raise result

    async def __aenter__(self):
        if self._closed:
            raise RuntimeError("Cannot reopen a client instance, once it has been closed.")

        return self

    async def __aexit__(self, exc_type=None, exc_value=None, traceback=None):
        await self.aclose()

    def _session_for(self, url, proxies, verify, cert):
        """Return the session for these request options, and whether to close it after the request."""

        if self._closed:
            raise RuntimeError("Cannot create a request session, as the client has been closed.")

        if verify is True or verify is None:
            # Resolve environment settings per request, before choosing a cached session.
            verify = (
                os.environ.get("REQUESTS_CA_BUNDLE")
                or os.environ.get("CURL_CA_BUNDLE")
                or True
            )
        elif not isinstance(verify, ssl.SSLContext):
            verify = os.fspath(verify) if verify else False
        if not cert:
            cert = None
        proxy = _select_proxy(url, proxies or {})
        if proxy is None and verify is True and cert is None:
            return self.session, False

        if cert is None or isinstance(cert, (str, bytes, os.PathLike)):
            cert_key = cert
        else:
            cert_key = tuple(cert)
        key = (proxy, verify, cert_key)

        session = self._option_sessions.get(key)
        if session is not None:
            return session, False

        session = self._create_session(proxy, verify, cert)
        if len(self._option_sessions) >= self._MAX_OPTION_SESSIONS:
            return session, True

        self._option_sessions[key] = session
        return session, False

    def _create_session(self, proxy=None, verify=None, cert=None):
        httpx2 = self._httpx2
        context = _ssl_context(httpx2, verify, cert)
        if proxy and proxy.startswith("https://"):
            # Like requests, verify the proxy with the request's settings, but only
            # offer the client certificate to the destination.
            proxy_context = _ssl_context(httpx2, verify, None) if cert else context
            proxy = httpx2.Proxy(proxy, ssl_context=proxy_context)

        return httpx2.AsyncClient(
            proxy=proxy,
            # Proxy selection and CA environment overrides use requests' rules instead.
            trust_env=False,
            verify=context,
            cookies=self.session.cookies.jar if hasattr(self, "session") else None,
            timeout=None,
            follow_redirects=True,
        )


def _read_body(body):
    """Return a request body that httpx2 can send asynchronously.

    requests streams file objects and iterators, but httpx2's AsyncClient only
    streams asynchronous iterators, so read them in full.
    """

    if isinstance(body, (str, bytes)):
        return body
    if hasattr(body, "read"):
        return body.read()
    if isinstance(body, (bytearray, memoryview)):
        return bytes(body)

    return b"".join(
        chunk.encode("utf-8") if isinstance(chunk, str) else chunk for chunk in body
    )


def _httpx2_timeout(httpx2, timeout):
    """Convert a requests timeout to an httpx2 timeout.

    requests applies a number to connecting and reading, and a ``(connect, read)``
    tuple to each one. It uses the connect timeout while sending the request,
    and doesn't limit the wait for a connection from the pool.
    """

    if isinstance(timeout, httpx2.Timeout):
        return timeout
    if isinstance(timeout, tuple):
        try:
            connect, read = timeout
        except ValueError:
            raise ValueError(
                f"Invalid timeout {timeout}. Pass a (connect, read) timeout tuple, "
                "or a single float to set both timeouts to the same value."
            )
    else:
        connect = read = timeout

    # Use requests' validation as httpx2 accepts zero, negative and boolean timeouts.
    requests.adapters.TimeoutSauce(connect=connect, read=read)
    return httpx2.Timeout(connect=connect, read=read, write=connect, pool=None)


def _select_proxy(url, proxies):
    """Choose the proxy for a URL as requests does. Returns None to connect directly."""

    proxies = dict(proxies)
    no_proxy = proxies.get("no_proxy")
    for scheme, proxy in requests.utils.get_environ_proxies(url, no_proxy=no_proxy).items():
        proxies.setdefault(scheme, proxy)

    # A proxy set to None disables the proxy from the environment for that scheme.
    proxies = {key: proxy for key, proxy in proxies.items() if proxy is not None}
    proxy = requests.utils.select_proxy(url, proxies)
    if proxy:
        return requests.utils.prepend_scheme_if_needed(proxy, "http")


def _ssl_context(httpx2, verify, cert):
    """Build the SSL context for requests-style verify and cert options."""

    if isinstance(verify, ssl.SSLContext):
        if cert:
            raise TypeError(
                "cert can't be combined with an SSLContext for verify. "
                "Load the certificate into the SSLContext with load_cert_chain() instead."
            )
        return verify

    if verify is None:
        # Like requests, use the CA bundle set in the environment, if any.
        verify = (
            os.environ.get("REQUESTS_CA_BUNDLE")
            or os.environ.get("CURL_CA_BUNDLE")
            or True
        )

    if verify is True:
        context = ssl.create_default_context(cafile=requests.certs.where())
    elif not verify:
        context = httpx2.create_ssl_context(verify=False, trust_env=False)
    elif not os.path.exists(verify):
        raise OSError(
            f"Could not find a suitable TLS CA certificate bundle, invalid path: {verify}"
        )
    elif os.path.isdir(verify):
        context = ssl.create_default_context(capath=verify)
    else:
        context = ssl.create_default_context(cafile=verify)

    if cert:
        if isinstance(cert, (str, bytes, os.PathLike)):
            context.load_cert_chain(cert)
        else:
            context.load_cert_chain(*cert)

    return context


def _connection_error(e):
    # httpx2 exceptions raise RuntimeError, rather than returning None, when they have no request.
    try:
        request = getattr(e, "request", None)
    except RuntimeError:
        request = None

    return HTTPConnectionError(requests.exceptions.ConnectionError(*e.args, request=request))


def _status_error(r):
    """Build the HTTPError requests would raise for an error status, without the API key in its URL."""

    kind = "Client" if r.status_code < 500 else "Server"
    url = r.url.copy_remove_param("api_key")
    message = f"{r.status_code} {kind} Error: {r.reason_phrase} for url: {url}"

    return HTTPError(requests.exceptions.HTTPError(message, response=r, request=r.request))
