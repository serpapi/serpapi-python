import asyncio
import logging
import os
import ssl
from collections.abc import Mapping
from contextlib import contextmanager
from urllib.parse import unquote_plus, urlencode, urlsplit
from weakref import ref

import requests
from urllib3.exceptions import LocationValueError
from urllib3.util import parse_url

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
    def __init__(self):
        # Only the async extra (Python 3.11+) needs contextvars.
        from contextvars import ContextVar

        super().__init__()
        self.active_request = ContextVar("serpapi_log_request", default=None)

    @contextmanager
    def for_request(self, request):
        token = self.active_request.set(ref(request))
        try:
            yield
        finally:
            self.active_request.reset(token)

    def filter(self, record):
        active = self.active_request.get()
        request = active() if active is not None else None
        args = record.args
        # A request hook can change this URL or issue an unrelated raw request.
        if (
            request is None or not isinstance(args, tuple)
            or len(args) < 2 or args[1] is not request.url
        ):
            return True

        url = urlsplit(str(request.url))
        fields = url.query.split("&")
        for i, field in enumerate(fields):
            name, sep, _ = field.partition("=")
            if sep and unquote_plus(name).lower() == "api_key":
                fields[i] = name + "=<redacted>"
        query = "&".join(fields)
        if query != url.query:
            record.args = (args[0], url._replace(query=query).geturl(), *args[2:])
        return True


def _protect_httpx2_logs():
    logger = logging.getLogger("httpx2")
    for item in logger.filters:
        if isinstance(item, _ApiKeyLogFilter):
            return item
    log_filter = _ApiKeyLogFilter()
    logger.addFilter(log_filter)
    return log_filter


def _asyncio_loop():
    try:
        return asyncio.get_running_loop()
    except RuntimeError:
        raise RuntimeError("serpapi.AsyncClient requires asyncio with a running event loop.") from None


class _RoutingTransport:
    """Dispatch SDK sends after native request hooks; raw session sends use the default pool."""

    def __init__(self, default):
        self.default = default
        self._routes = {}

    @contextmanager
    def route(self, request, select):
        key = (asyncio.current_task(), id(request))
        self._routes[key] = select
        try:
            yield
        finally:
            del self._routes[key]

    async def handle_async_request(self, request):
        select = self._routes.get((asyncio.current_task(), id(request)))
        transport = self.default if select is None else select(str(request.url))
        return await transport.handle_async_request(request)

    async def __aenter__(self):
        await self.default.__aenter__()
        return self

    async def __aexit__(self, *exc_info):
        await self.default.__aexit__(*exc_info)

    async def aclose(self):
        await self.default.aclose()


class AsyncHTTPClient:
    """This class handles outgoing asynchronous HTTP requests to SerpApi.com.

    It uses an ``httpx2.AsyncClient`` and accepts the same request options as
    :class:`HTTPClient`, which uses ``requests``.
    """

    BASE_DOMAIN = HTTPClient.BASE_DOMAIN
    USER_AGENT = HTTPClient.USER_AGENT

    _MAX_OPTION_POOLS = 16
    _MAX_SSL_CONTEXTS = 16

    def __init__(self, *, api_key=None, timeout=None):
        self._httpx2 = _import_httpx2()
        self._log_filter = _protect_httpx2_logs()
        self.api_key = api_key
        self.timeout = timeout
        self._closed = False
        self._close_task = None
        self._option_pools = {}
        self._ssl_contexts = {}
        self._default_ssl_context = _ssl_context(self._httpx2, True, None)
        self._router = _RoutingTransport(self._create_pool(verify=True))
        self.session = self._httpx2.AsyncClient(
            transport=self._router, trust_env=False, timeout=None, follow_redirects=True
        )

    def _check_can_request(self):
        _asyncio_loop()
        if self._closed:
            raise RuntimeError("Cannot send a request, as the client has been closed.")

    async def request(self, method, path, params, *, assert_200=True, **kwargs):
        httpx2 = self._httpx2
        self._check_can_request()

        # Inject the API Key into the params.
        api_key_in_data = _form_has_api_key(kwargs.get("data"))
        if self.api_key is not None and not api_key_in_data and not _has_api_key(params):
            params = {**params, "api_key": self.api_key}

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
        try:
            auth = kwargs.pop("auth", httpx2.USE_CLIENT_DEFAULT)
            request = self.session.build_request(method, prepared.url, headers=headers, **kwargs)
            if self.session.params:
                # build_request replaces the entire query when the session has defaults.
                request.url = _with_query_defaults(
                    httpx2.URL(prepared.url), self.session.params, params, api_key_in_data
                )
            r = await self._send_with_auth(request, auth, follow_redirects, proxies, verify, cert)
        except httpx2.ConnectTimeout as e:
            # requests reports connection timeouts as connection errors.
            raise _connection_error(e) from e
        except httpx2.TimeoutException as e:
            raise TimeoutError(str(e) or "The request timed out.") from e
        except (
            httpx2.NetworkError, httpx2.ProtocolError, httpx2.ProxyError, ssl.SSLError
        ) as e:
            raise _connection_error(e) from e
        except httpx2.DecodingError as e:
            raise requests.exceptions.ContentDecodingError(str(e)) from e
        except httpx2.TooManyRedirects as e:
            raise requests.exceptions.TooManyRedirects(str(e), request=_error_request(e)) from e
        except httpx2.UnsupportedProtocol as e:
            raise requests.exceptions.InvalidSchema(str(e), request=_error_request(e)) from e
        except httpx2.HTTPError as e:
            raise requests.exceptions.RequestException(
                str(e), request=_error_request(e), response=getattr(e, "response", None)
            ) from e

        # Raise an exception if the status code is not 200.
        if assert_200 and 400 <= r.status_code < 600:
            raise _status_error(r)

        return r

    async def _send_with_auth(self, request, auth, follow_redirects, proxies, verify, cert):
        from contextlib import AsyncExitStack, aclosing

        # Match httpx2's ordering: select auth once (including session defaults and
        # URL credentials), then give it the response *after* following redirects.
        auth = _request_auth(self._httpx2, self.session, request, auth)
        auth_history = []
        redirects = []
        async with aclosing(auth.async_auth_flow(request)) as flow:
            request = await flow.__anext__()
            while True:
                async with AsyncExitStack() as cleanup:
                    response = await self._open_response(request, proxies, verify, cert, cleanup)
                    response.history = auth_history + redirects
                    # Like requests, an empty Location header ends redirect handling.
                    location = response.headers.get("Location")
                    if follow_redirects and response.has_redirect_location and location:
                        await response.aread()
                        if len(redirects) >= requests.models.DEFAULT_REDIRECT_LIMIT:
                            raise requests.exceptions.TooManyRedirects(
                                f"Exceeded {len(redirects)} redirects.",
                                response=response, request=request,
                            )
                        next_request = _redirect_request(request, response)
                        # httpx2 only keeps next_request on redirects that it does not follow.
                        response.next_request = None
                        redirects.append(response)
                        request = next_request
                    else:
                        # Auth can reject the status or headers without reading the body.
                        try:
                            request = await flow.asend(response)
                        except StopAsyncIteration:
                            await response.aread()
                            return response
                        response.history = list(auth_history)
                        await response.aread()
                        auth_history.append(response)
                        redirects.clear()
                if len(auth_history) > self.session.max_redirects:
                    raise self._httpx2.TooManyRedirects(
                        "Exceeded maximum allowed redirects.", request=request
                    )

    async def _open_response(self, request, proxies, verify, cert, cleanup):
        def select(url):
            pool, temporary = self._pool_for(url, proxies, verify, cert)
            if temporary:
                cleanup.push_async_callback(pool.aclose)
            return pool

        with self._router.route(request, select), self._log_filter.for_request(request):
            # An explicit no-op, not auth=None: the latter can still apply URL credentials.
            response = await self.session.send(
                request, auth=self._httpx2.Auth(), follow_redirects=False, stream=True
            )
        cleanup.push_async_callback(response.aclose)
        return response

    async def aclose(self):
        """Close the client's HTTP connections. The client cannot send requests afterwards."""

        loop = _asyncio_loop()
        self._closed = True
        if self._close_task is None:
            # Close in a task, so that the sessions still close if the caller is cancelled.
            self._close_task = loop.create_task(self._close_pools())
            self._close_task.add_done_callback(self._after_close)

        await asyncio.shield(self._close_task)

    def _after_close(self, close_task):
        self._close_task = None
        # Reading the exception also stops asyncio reporting it as never retrieved.
        if not close_task.cancelled() and close_task.exception() is None:
            self._option_pools.clear()

    async def _close_pools(self):
        resources = [self.session, *self._option_pools.values()]
        results = await asyncio.gather(
            *(resource.aclose() for resource in resources), return_exceptions=True
        )
        for result in results:
            if isinstance(result, asyncio.CancelledError):
                raise result
            if isinstance(result, Exception):
                raise result

    async def __aenter__(self):
        _asyncio_loop()
        if self._closed:
            raise RuntimeError("Cannot reopen a client instance, once it has been closed.")

        return self

    async def __aexit__(self, exc_type=None, exc_value=None, traceback=None):
        await self.aclose()

    def _pool_for(self, url, proxies, verify, cert):
        """Return the transport for this destination and whether it is temporary."""

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
            return self._router.default, False

        key = (proxy, verify, _cert_key(cert))

        pool = self._option_pools.get(key)
        if pool is not None:
            return pool, False

        pool = self._create_pool(proxy, verify, cert)
        if len(self._option_pools) >= self._MAX_OPTION_POOLS:
            return pool, True

        self._option_pools[key] = pool
        return pool, False

    def _session_ssl_context(self, verify, cert):
        if verify is True and not cert:
            return self._default_ssl_context
        if isinstance(verify, ssl.SSLContext):
            return _ssl_context(self._httpx2, verify, cert)

        # Load each CA bundle and certificate once, even for proxies and temporary pools.
        key = (verify, _cert_key(cert))
        context = self._ssl_contexts.get(key)
        if context is None:
            context = _ssl_context(self._httpx2, verify, cert)
            if len(self._ssl_contexts) < self._MAX_SSL_CONTEXTS:
                self._ssl_contexts[key] = context
        return context

    def _create_pool(self, proxy=None, verify=None, cert=None):
        httpx2 = self._httpx2
        context = self._session_ssl_context(verify, cert)
        if proxy and proxy.startswith("https://"):
            # Like requests, verify the proxy with the request's settings, but only
            # offer the client certificate to the destination.
            proxy_context = self._session_ssl_context(verify, None) if cert else context
            proxy = httpx2.Proxy(proxy, ssl_context=proxy_context)

        return httpx2.AsyncHTTPTransport(
            proxy=proxy,
            # Proxy selection and CA environment overrides use requests' rules instead.
            trust_env=False,
            verify=context,
        )


def _has_api_key(names):
    return "api_key" in names or b"api_key" in names


def _form_has_api_key(data):
    if isinstance(data, Mapping):
        return _has_api_key(data)
    if isinstance(data, (list, tuple)):
        # Inspect ordinary form pairs without touching file objects or iterators.
        return any(
            isinstance(pair, (list, tuple)) and pair and pair[0] in ("api_key", b"api_key")
            for pair in data
        )
    return False


def _with_query_defaults(url, defaults, params, api_key_in_data):
    # Explicit None suppresses a default even though it isn't in the encoded URL.
    specified = set(url.params).union(params)
    if api_key_in_data:
        specified.add("api_key")
    missing = [
        (k, v) for k, v in defaults.multi_items()
        if k not in specified and k.encode("utf-8") not in specified
    ]
    if not missing:
        return url
    suffix = urlencode(missing).encode("ascii")
    return url.copy_with(query=url.query + b"&" + suffix if url.query else suffix)


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


def _cert_key(cert):
    if cert is None or isinstance(cert, (str, bytes, os.PathLike)):
        return cert
    return tuple(cert)


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


def _request_auth(httpx2, session, request, auth):
    """Select a request's auth like httpx2's client does, using only public httpx2 API."""

    if isinstance(auth, type(httpx2.USE_CLIENT_DEFAULT)):
        auth = session.auth
    elif isinstance(auth, tuple):
        auth = httpx2.BasicAuth(username=auth[0], password=auth[1])
    elif auth is not None and not isinstance(auth, httpx2.Auth):
        if not callable(auth):
            raise TypeError(f'Invalid "auth" argument: {auth!r}')
        auth = httpx2.FunctionAuth(func=auth)
    if auth is not None:
        return auth

    username, password = request.url.username, request.url.password
    if username or password:
        return httpx2.BasicAuth(username=username, password=password)
    return httpx2.Auth()


def _error_request(e):
    # httpx2 exceptions raise RuntimeError, rather than returning None, when they have no request.
    try:
        return getattr(e, "request", None)
    except RuntimeError:
        return None


def _redirect_request(request, response):
    """Return the next redirect request, or raise the error requests raises for its target."""

    next_request = response.next_request
    if next_request is None:
        # httpx2 builds no next request when the Location header is not a valid URL.
        try:
            scheme = urlsplit(response.headers["Location"]).scheme.lower()
        except ValueError:
            scheme = ""
        if scheme and scheme not in ("http", "https"):
            raise requests.exceptions.InvalidSchema(
                "No connection adapters were found for the redirect location.",
                request=request, response=response,
            )
        raise requests.exceptions.InvalidURL(
            "Invalid URL in the redirect location header.", request=request, response=response
        )

    # requests rejects URLs that urllib3 cannot parse, such as ports above 65535.
    try:
        parse_url(str(next_request.url))
    except LocationValueError:
        raise requests.exceptions.InvalidURL(
            "Invalid URL in the redirect location header.", request=request, response=response
        ) from None
    return next_request


def _connection_error(e):
    return HTTPConnectionError(requests.exceptions.ConnectionError(*e.args, request=_error_request(e)))


def _status_error(r):
    """Build the HTTPError requests would raise for an error status, without the API key in its URL."""

    kind = "Client" if r.status_code < 500 else "Server"
    url = r.url.copy_remove_param("api_key")
    message = f"{r.status_code} {kind} Error: {r.reason_phrase} for url: {url}"

    return HTTPError(requests.exceptions.HTTPError(message, response=r, request=r.request))
