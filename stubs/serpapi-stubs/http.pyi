from typing import Any, Mapping, MutableMapping, Optional, Tuple, Union

import requests
from typing_extensions import TypeAlias

_Timeout: TypeAlias = Union[None, float, Tuple[Optional[float], Optional[float]]]
_Proxies: TypeAlias = Union[None, Mapping[str, str]]
_Verify: TypeAlias = Union[None, bool, str]
_Cert: TypeAlias = Union[None, str, Tuple[str, str]]

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
