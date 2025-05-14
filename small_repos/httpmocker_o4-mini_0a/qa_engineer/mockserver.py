import re
import json
import base64
import time
from typing import Callable, Any, Dict, List

class Request:
    def __init__(self, method, path, headers=None, query_params=None, body=None):
        self.method = method.upper()
        self.path = path
        self.headers = headers or {}
        self.query_params = query_params or {}
        self.body = body

class Response:
    def __init__(self, status_code=200, headers=None, body=None):
        self.status_code = status_code
        self.headers = headers or {}
        self.body = body

class MockWebSocket:
    def __init__(self):
        self.messages = []
        self.error = None

    def send(self, message):
        if self.error:
            raise self.error
        self.messages.append(message)

    def receive(self):
        if self.error:
            raise self.error
        return self.messages.pop(0) if self.messages else None

    def simulateError(self, error):
        self.error = error

class MockServer:
    def __init__(self):
        self.handlers = []  # list of (method, path, pattern, handler)
        self.cors = None
        self.rate_limits = {}  # identifier -> {limit, window, count, reset}

    def registerEndpoint(self, method: str, path: str, handler: Callable):
        pattern = re.compile(path) if path.startswith('^') else None
        self.handlers.append((method.upper(), path, pattern, handler))

    def hotReloadHandlers(self, endpoints: List[tuple]):
        self.handlers = []
        for method, path, handler in endpoints:
            self.registerEndpoint(method, path, handler)

    def configureCORS(self, allow_origin='*', allow_methods=None, allow_headers=None):
        self.cors = {
            'Access-Control-Allow-Origin': allow_origin,
            'Access-Control-Allow-Methods': ','.join(allow_methods) if allow_methods else '*',
            'Access-Control-Allow-Headers': ','.join(allow_headers) if allow_headers else '*'
        }

    def simulateRateLimiting(self, identifier, limit: int, window: int):
        self.rate_limits[identifier] = {
            'limit': limit,
            'window': window,
            'count': 0,
            'reset': time.time() + window
        }

    def mockWebSocket(self, path: str, handler: Callable[[MockWebSocket], Any]):
        def ws_handler(request):
            ws = MockWebSocket()
            result = handler(ws)
            return result or ws
        self.registerEndpoint('GET', path, ws_handler)

    def handleRequest(self, request: Request) -> Any:
        if request.method == 'OPTIONS' and self.cors:
            return Response(204, headers=self.cors)
        for method, path, pattern, handler in self.handlers:
            if method != request.method:
                continue
            if pattern:
                if pattern.match(request.path):
                    return self._invokeHandler(handler, request)
            else:
                if path == request.path:
                    return self._invokeHandler(handler, request)
        return Response(404, body='Not Found')

    def _invokeHandler(self, handler, request):
        # Rate limiting
        identifier = request.headers.get('X-RateLimit-User', None)
        if identifier and identifier in self.rate_limits:
            rl = self.rate_limits[identifier]
            now = time.time()
            if now > rl['reset']:
                rl['count'] = 0
                rl['reset'] = now + rl['window']
            if rl['count'] >= rl['limit']:
                retry_after = int(rl['reset'] - now)
                return Response(429, headers={'Retry-After': str(retry_after)}, body='Too Many Requests')
            rl['count'] += 1
        resp = handler(request)
        if not isinstance(resp, Response):
            return resp
        if self.cors:
            resp.headers.update(self.cors)
        return resp

def assertHeader(name, expected=None):
    def decorator(handler):
        def wrapper(request):
            val = request.headers.get(name)
            if val is None:
                raise AssertionError(f'Missing header {name}')
            if expected is not None:
                if hasattr(expected, 'match'):
                    if not expected.match(val):
                        raise AssertionError(f'Header {name} value {val} does not match pattern')
                elif val != expected:
                    raise AssertionError(f'Header {name} value {val} != expected {expected}')
            return handler(request)
        return wrapper
    return decorator

def assertQueryParam(name, expected=None):
    def decorator(handler):
        def wrapper(request):
            val = request.query_params.get(name)
            if val is None:
                raise AssertionError(f'Missing query param {name}')
            if expected is not None:
                if hasattr(expected, 'match'):
                    if not expected.match(val):
                        raise AssertionError(f'Query param {name} value {val} does not match pattern')
                elif val != expected:
                    raise AssertionError(f'Query param {name} value {val} != expected {expected}')
            return handler(request)
        return wrapper
    return decorator

def assertBody(schema=None, predicate=None):
    def decorator(handler):
        def wrapper(request):
            data = None
            if request.body is not None:
                try:
                    data = json.loads(request.body)
                except Exception:
                    raise AssertionError('Invalid JSON body')
            if schema:
                required = schema.get('required', [])
                if data is None:
                    raise AssertionError('Missing JSON body')
                for key in required:
                    if key not in data:
                        raise AssertionError(f'Missing body field {key}')
            if predicate:
                if not predicate(data):
                    raise AssertionError('Body predicate failed')
            return handler(request)
        return wrapper
    return decorator

def simulateAuth(auth_type, valid_credentials):
    def decorator(handler):
        def wrapper(request):
            auth = request.headers.get('Authorization')
            t = auth_type.lower()
            if t == 'basic':
                if not auth or not auth.startswith('Basic '):
                    return Response(401, headers={'WWW-Authenticate': 'Basic'}, body='Unauthorized')
                token = auth.split(' ',1)[1]
                try:
                    decoded = base64.b64decode(token).decode()
                except Exception:
                    return Response(400, body='Bad Request')
                if decoded not in valid_credentials:
                    return Response(403, body='Forbidden')
            elif t == 'bearer':
                if not auth or not auth.startswith('Bearer '):
                    return Response(401, headers={'WWW-Authenticate': 'Bearer'}, body='Unauthorized')
                token = auth.split(' ',1)[1]
                if token not in valid_credentials:
                    return Response(403, body='Forbidden')
            return handler(request)
        return wrapper
    return decorator

def simulateChunkedTransfer(chunk_generator):
    def decorator(handler):
        def wrapper(request):
            resp = handler(request)
            if not isinstance(resp, Response):
                return resp
            body = resp.body
            resp.body = chunk_generator(body)
            resp.headers['Transfer-Encoding'] = 'chunked'
            return resp
        return wrapper
    return decorator
