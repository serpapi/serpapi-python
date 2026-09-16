import os
import ssl
from collections.abc import Mapping
from urllib.parse import urlsplit, urlunsplit

import httpx

from .__version__ import __version__
from .exceptions import HTTPConnectionError, HTTPError, TimeoutError

REQUEST_OPTIONS = ("timeout", "proxies", "verify", "stream", "cert")
_UNSET = object()


def _ssl_configuration(verify=True, cert=None):
    """Translate requests-style TLS options into an HTTPX configuration."""
    if cert is None and not isinstance(verify, (str, os.PathLike)):
        return verify

    if isinstance(verify, ssl.SSLContext):
        context = verify
    elif verify is False:
        context = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
        context.check_hostname = False
        context.verify_mode = ssl.CERT_NONE
    elif isinstance(verify, (str, os.PathLike)):
        context = ssl.create_default_context(cafile=os.fspath(verify))
    else:
        context = ssl.create_default_context()

    if cert is not None:
        if isinstance(cert, (tuple, list)):
            context.load_cert_chain(os.fspath(cert[0]), os.fspath(cert[1]))
        else:
            context.load_cert_chain(os.fspath(cert))

    return context


def _proxy_configuration(proxies, *, asynchronous, verify):
    if not isinstance(proxies, Mapping):
        return {"proxy": proxies}

    transport_class = httpx.AsyncHTTPTransport if asynchronous else httpx.HTTPTransport
    mounts = {}
    for scheme, proxy_url in proxies.items():
        mount = scheme if "://" in scheme else f"{scheme}://"
        mounts[mount] = (
            None
            if proxy_url is None
            else transport_class(proxy=proxy_url, verify=verify)
        )
    return {"mounts": mounts}


class _HTTPClientBase:
    """Shared request preparation for synchronous and asynchronous clients."""

    BASE_DOMAIN = "https://serpapi.com"
    USER_AGENT = f"serpapi-python, v{__version__}"

    def __init__(
        self,
        *,
        api_key=None,
        timeout=None,
        proxy=None,
        verify=True,
        cert=None,
        trust_env=True,
    ):
        self.api_key = api_key
        self.timeout = timeout
        self._proxy = proxy
        self._verify = verify
        self._cert = cert
        self._trust_env = trust_env

    def _client_options(
        self, *, asynchronous, proxies=_UNSET, verify=_UNSET, cert=_UNSET
    ):
        selected_verify = self._verify if verify is _UNSET else verify
        selected_cert = self._cert if cert is _UNSET else cert
        ssl_config = _ssl_configuration(selected_verify, selected_cert)
        options = {
            "headers": {"User-Agent": self.USER_AGENT},
            "timeout": self.timeout,
            "follow_redirects": True,
            "trust_env": self._trust_env,
            "verify": ssl_config,
        }

        selected_proxy = self._proxy if proxies is _UNSET else proxies
        if selected_proxy is not None:
            options.update(
                _proxy_configuration(
                    selected_proxy,
                    asynchronous=asynchronous,
                    verify=ssl_config,
                )
            )
        return options

    def _prepare_request(self, path, params, kwargs):
        request_data = kwargs.get("data")
        api_key_in_data = isinstance(request_data, dict) and "api_key" in request_data
        if "api_key" not in params and not api_key_in_data:
            params["api_key"] = self.api_key

        # Match requests: query parameters with a None value are omitted.
        params = {key: value for key, value in params.items() if value is not None}
        url = path if path.startswith("http") else self.BASE_DOMAIN + path
        parsed_url = urlsplit(url)
        if parsed_url.query:
            params = httpx.QueryParams(parsed_url.query).merge(params)
            url = urlunsplit(parsed_url._replace(query=""))

        if self.timeout is not None and "timeout" not in kwargs:
            kwargs["timeout"] = self.timeout

        # SDK endpoint methods always consume the response before returning.
        # Accept the old option for compatibility, but use HTTPX's safe,
        # fully-buffered request behavior.
        kwargs.pop("stream", None)

        connection_options = {}
        for key in ("proxies", "verify", "cert"):
            if key in kwargs:
                connection_options[key] = kwargs.pop(key)

        return url, params, kwargs, connection_options


class HTTPClient(_HTTPClientBase):
    """Synchronous HTTP transport with connection pooling."""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.session = httpx.Client(**self._client_options(asynchronous=False))

    def request(self, method, path, params, *, assert_200=True, **kwargs):
        url, params, kwargs, connection_options = self._prepare_request(
            path, params, kwargs
        )
        try:
            if connection_options:
                options = self._client_options(
                    asynchronous=False,
                    proxies=connection_options.get("proxies", _UNSET),
                    verify=connection_options.get("verify", _UNSET),
                    cert=connection_options.get("cert", _UNSET),
                )
                with httpx.Client(**options) as session:
                    response = session.request(
                        method=method,
                        url=url,
                        params=params,
                        headers={"User-Agent": self.USER_AGENT},
                        **kwargs,
                    )
            else:
                response = self.session.request(
                    method=method,
                    url=url,
                    params=params,
                    headers={"User-Agent": self.USER_AGENT},
                    **kwargs,
                )
        except httpx.TimeoutException as exc:
            raise TimeoutError(exc) from exc
        except httpx.RequestError as exc:
            raise HTTPConnectionError(exc) from exc

        if assert_200:
            raise_for_status(response)
        return response

    def close(self):
        self.session.close()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.close()


class AsyncHTTPClient(_HTTPClientBase):
    """Asynchronous HTTP transport with connection pooling."""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.session = httpx.AsyncClient(**self._client_options(asynchronous=True))

    async def request(self, method, path, params, *, assert_200=True, **kwargs):
        url, params, kwargs, connection_options = self._prepare_request(
            path, params, kwargs
        )
        try:
            if connection_options:
                options = self._client_options(
                    asynchronous=True,
                    proxies=connection_options.get("proxies", _UNSET),
                    verify=connection_options.get("verify", _UNSET),
                    cert=connection_options.get("cert", _UNSET),
                )
                async with httpx.AsyncClient(**options) as session:
                    response = await session.request(
                        method=method,
                        url=url,
                        params=params,
                        headers={"User-Agent": self.USER_AGENT},
                        **kwargs,
                    )
            else:
                response = await self.session.request(
                    method=method,
                    url=url,
                    params=params,
                    headers={"User-Agent": self.USER_AGENT},
                    **kwargs,
                )
        except httpx.TimeoutException as exc:
            raise TimeoutError(exc) from exc
        except httpx.RequestError as exc:
            raise HTTPConnectionError(exc) from exc

        if assert_200:
            raise_for_status(response)
        return response

    async def aclose(self):
        await self.session.aclose()

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_value, traceback):
        await self.aclose()


def raise_for_status(response):
    """Raise the SerpApi HTTP error type for unsuccessful responses."""
    try:
        response.raise_for_status()
    except httpx.HTTPStatusError as exc:
        raise HTTPError(exc) from exc
