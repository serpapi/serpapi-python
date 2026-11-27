from os import PathLike
from ssl import SSLContext
from types import TracebackType
from typing import Any, Mapping, MutableMapping, Optional, Tuple, Type, Union

import httpx2
import requests
from typing_extensions import Self, TypeAlias

_Timeout: TypeAlias = Union[None, float, Tuple[Optional[float], Optional[float]]]
# requests mutates proxies when merging the environment; None opts out of a configured proxy.
_Proxies: TypeAlias = Union[
    None, MutableMapping[str, str], MutableMapping[str, None], MutableMapping[str, Optional[str]]
]
_Verify: TypeAlias = Union[None, bool, str]
_Cert: TypeAlias = Union[None, str, Tuple[str, str]]
_Path: TypeAlias = Union[str, bytes, PathLike[str], PathLike[bytes]]
_AsyncTimeout: TypeAlias = Union[_Timeout, httpx2.Timeout]
_AsyncProxies: TypeAlias = Optional[Mapping[str, Optional[str]]]
_AsyncVerify: TypeAlias = Union[None, bool, _Path, SSLContext]
_AsyncCert: TypeAlias = Union[None, _Path, Tuple[_Path, _Path]]

class HTTPClient:
    BASE_DOMAIN: str
    USER_AGENT: str
    api_key: Optional[str]
    timeout: _Timeout
    session: requests.Session
    def __init__(self, *, api_key: Optional[str] = None, timeout: _Timeout = None) -> None: ...
    def request(
        self,
        method: str,
        path: str,
        params: MutableMapping[str, Any],
        *,
        assert_200: bool = True,
        **kwargs: Any,
    ) -> requests.Response: ...

def raise_for_status(r: requests.Response) -> None: ...

class AsyncHTTPClient:
    BASE_DOMAIN: str
    USER_AGENT: str
    api_key: Optional[str]
    timeout: _AsyncTimeout
    session: httpx2.AsyncClient
    def __init__(self, *, api_key: Optional[str] = None, timeout: _AsyncTimeout = None) -> None: ...
    async def request(
        self,
        method: str,
        path: str,
        params: Mapping[str, Any],
        *,
        assert_200: bool = True,
        **kwargs: Any,
    ) -> httpx2.Response: ...
    async def aclose(self) -> None: ...
    async def __aenter__(self) -> Self: ...
    async def __aexit__(
        self,
        exc_type: Optional[Type[BaseException]] = None,
        exc_value: Optional[BaseException] = None,
        traceback: Optional[TracebackType] = None,
    ) -> None: ...
