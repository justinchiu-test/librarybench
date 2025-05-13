import time
from typing import Optional, Dict, Any
from mock_server import MockServer, Response

class HttpClient:
    def __init__(self, server: MockServer):
        self.server = server
        self.retry_policies = {}  # type: Dict[(str,str), (int, float)]

    def setRetryPolicy(self, method: str, path: str, retries: int, backoff: float):
        self.retry_policies[(method.upper(), path)] = (retries, backoff)

    def _request(self, method: str, path: str,
                 headers: Optional[Dict[str, str]] = None,
                 params: Optional[Dict[str, str]] = None,
                 timeout: Optional[float] = None,
                 body: Any = None) -> Response:
        retries, backoff = self.retry_policies.get((method.upper(), path), (0, 0))
        attempt = 0
        while True:
            try:
                return self.server.handle_request(method, path, headers, params, body)
            except (TimeoutError, ConnectionResetError) as e:
                if attempt < retries:
                    attempt += 1
                    time.sleep(backoff)
                    continue
                else:
                    raise

    def get(self, path: str,
            headers: Optional[Dict[str, str]] = None,
            params: Optional[Dict[str, str]] = None,
            timeout: Optional[float] = None) -> Response:
        return self._request('GET', path, headers, params, timeout, None)

    def post(self, path: str,
             headers: Optional[Dict[str, str]] = None,
             params: Optional[Dict[str, str]] = None,
             timeout: Optional[float] = None,
             body: Any = None) -> Response:
        return self._request('POST', path, headers, params, timeout, body)

    def put(self, path: str,
            headers: Optional[Dict[str, str]] = None,
            params: Optional[Dict[str, str]] = None,
            timeout: Optional[float] = None,
            body: Any = None) -> Response:
        return self._request('PUT', path, headers, params, timeout, body)

    def delete(self, path: str,
               headers: Optional[Dict[str, str]] = None,
               params: Optional[Dict[str, str]] = None,
               timeout: Optional[float] = None) -> Response:
        return self._request('DELETE', path, headers, params, timeout, None)
