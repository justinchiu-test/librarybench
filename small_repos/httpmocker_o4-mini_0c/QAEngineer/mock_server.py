import re
import json
from typing import Callable, Optional, Dict, Any, Tuple

class Request:
    def __init__(self, method: str, path: str, headers: Optional[Dict[str, str]] = None,
                 params: Optional[Dict[str, str]] = None, body: Any = None):
        self.method = method.upper()
        self.path = path
        self.headers = headers or {}
        self.params = params or {}
        self.body = body

class Response:
    def __init__(self, status_code: int = 200, headers: Optional[Dict[str, str]] = None, body: Any = None):
        self.status_code = status_code
        self.headers = headers or {}
        self.body = body

class MockServer:
    def __init__(self):
        self.recording = False
        self.requests = []  # type: list[Request]
        self.endpoints = {}  # type: Dict[Tuple[str,str], Dict[str, Any]]
        self.error_simulations = {}  # type: Dict[Tuple[str,str], str]
        self.cors_config = None  # type: Dict[str, str]

    def startRequestRecording(self):
        self.recording = True

    def _record(self, req: Request):
        if self.recording:
            self.requests.append(req)

    def registerEndpoint(self, method: str, path: str, handler: Callable[[Request], Response]):
        self.endpoints[(method.upper(), path)] = {'handler': handler}

    def addDynamicCallback(self, method: str, path: str, callback: Callable[[Request], Response]):
        key = (method.upper(), path)
        if key not in self.endpoints:
            self.endpoints[key] = {}
        self.endpoints[key]['callback'] = callback

    def simulateError(self, method: str, path: str, error_type: str):
        self.error_simulations[(method.upper(), path)] = error_type

    def configureCORS(self, headers: Dict[str, str]):
        self.cors_config = headers

    def assertHeader(self, req: Request, header: str,
                     value: Optional[str] = None, regex: Optional[bool] = False):
        if header not in req.headers:
            raise AssertionError(f"Header '{header}' not present")
        if value is not None:
            actual = req.headers.get(header)
            if regex:
                if not re.match(value, actual or ""):
                    raise AssertionError(f"Header '{header}' value '{actual}' does not match regex '{value}'")
            else:
                if actual != value:
                    raise AssertionError(f"Header '{header}' value '{actual}' != '{value}'")

    def assertRequestBody(self, req: Request,
                          schema: Optional[Dict[str, type]] = None,
                          predicate: Optional[Callable[[Any], bool]] = None):
        body = req.body
        if schema is not None:
            if not isinstance(body, dict):
                raise AssertionError("Body is not a JSON object")
            for key, typ in schema.items():
                if key not in body:
                    raise AssertionError(f"Missing key in body: {key}")
                if not isinstance(body[key], typ):
                    raise AssertionError(f"Key '{key}' is not of type {typ}")
        if predicate is not None:
            if not predicate(body):
                raise AssertionError("Body predicate returned False")

    def handle_request(self, method: str, path: str,
                       headers: Optional[Dict[str, str]] = None,
                       params: Optional[Dict[str, str]] = None,
                       body: Any = None) -> Response:
        req = Request(method, path, headers, params, body)
        self._record(req)
        # Handle CORS preflight
        if self.cors_config and req.method == 'OPTIONS':
            resp = Response(200, headers=self.cors_config.copy(), body="")
            return resp
        # Simulate error if configured
        err = self.error_simulations.get((req.method, req.path))
        if err:
            if err.startswith('5'):
                return Response(int(err), headers={}, body="")
            if err == 'timeout':
                raise TimeoutError("Simulated timeout")
            if err == 'connection_reset':
                raise ConnectionResetError("Simulated connection reset")
            if err == 'malformed':
                return Response(200, headers={}, body="<<malformed>>")
        # Find endpoint
        ep = self.endpoints.get((req.method, req.path))
        if not ep or 'handler' not in ep:
            return Response(404, headers={}, body="Not Found")
        handler = ep['handler']
        # Inject json into handler's globals so test handlers can use json.dumps
        try:
            handler.__globals__['json'] = json
        except Exception:
            pass
        # Execute handler
        resp = handler(req)
        # Apply dynamic callback if present
        cb = ep.get('callback')
        if cb:
            try:
                cb.__globals__['json'] = json
            except Exception:
                pass
            return cb(req)
        return resp
