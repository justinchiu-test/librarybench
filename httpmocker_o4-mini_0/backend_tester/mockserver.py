import re
import json
import threading
import time
from http import HTTPStatus

try:
    import jsonschema
except ImportError:
    jsonschema = None

class Response:
    def __init__(self, status_code=200, headers=None, body=None, chunks=None):
        self.status_code = status_code
        self.headers = headers or {}
        self.body = body
        self._chunks = chunks

    def iter_chunks(self):
        if self._chunks:
            for chunk in self._chunks:
                yield chunk
        else:
            yield self.body or b''

class Request:
    def __init__(self, method, path, headers=None, body=None):
        self.method = method.upper()
        parts = path.split('?', 1)
        self.path = parts[0]
        self.query = {}
        if len(parts) > 1:
            for kv in parts[1].split('&'):
                if '=' in kv:
                    k, v = kv.split('=', 1)
                else:
                    k, v = kv, ''
                self.query.setdefault(k, []).append(v)
        self.headers = headers or {}
        self.body = body

class MockServer:
    def __init__(self):
        self._endpoints = []
        self._cors = None
        self._auth = None
        self._rate_limits = {}
        self._lock = threading.Lock()
        self._ws = MockWebSocket()

    def registerEndpoint(self, method, path, handler):
        pattern = path
        if isinstance(path, str) and (path.startswith('^') or '(' in path or '.' in path):
            pattern = re.compile(path)
        self._endpoints = [e for e in self._endpoints if not (e['method']==method.upper() and e['path']==path)]
        self._endpoints.append({'method': method.upper(), 'path': pattern, 'handler': handler})

    def hotReloadHandlers(self, endpoints):
        with self._lock:
            self._endpoints = []
            for method, path, handler in endpoints:
                self.registerEndpoint(method, path, handler)

    def configureCORS(self, origin='*', methods=None, headers=None, max_age=3600):
        self._cors = {
            'Access-Control-Allow-Origin': origin,
            'Access-Control-Allow-Methods': ','.join(methods) if methods else '*',
            'Access-Control-Allow-Headers': ','.join(headers) if headers else '*',
            'Access-Control-Max-Age': str(max_age)
        }

    def simulateAuth(self, scheme, validator):
        self._auth = {'scheme': scheme.lower(), 'validator': validator}

    def simulateRateLimiting(self, method, path, limit, window):
        key = (method.upper(), path)
        self._rate_limits[key] = {'limit': limit, 'window': window, 'calls': []}

    @staticmethod
    def assertHeader(headers, name, expected):
        if name not in headers:
            raise AssertionError(f"Header '{name}' not found")
        val = headers[name]
        if hasattr(expected, 'match'):
            if not expected.match(val):
                raise AssertionError(f"Header '{name}' value '{val}' does not match {expected}")
        elif callable(expected):
            if not expected(val):
                raise AssertionError(f"Header '{name}' value '{val}' did not satisfy predicate")
        else:
            if val != expected:
                raise AssertionError(f"Header '{name}' expected '{expected}', got '{val}'")

    @staticmethod
    def assertBody(body, expected):
        if callable(expected):
            if not expected(body):
                raise AssertionError("Body predicate returned False")
        else:
            if jsonschema:
                jsonschema.validate(instance=body, schema=expected)
            else:
                if body != expected:
                    raise AssertionError(f"Body does not match schema, expected {expected}")

    @staticmethod
    def assertQueryParam(query, name, expected):
        if name not in query:
            raise AssertionError(f"Query param '{name}' not found")
        vals = query[name]
        for v in vals:
            if hasattr(expected, 'match'):
                if not expected.match(v):
                    raise AssertionError(f"Query param '{name}' value '{v}' does not match {expected}")
            elif callable(expected):
                if not expected(v):
                    raise AssertionError(f"Query param '{name}' value '{v}' failed predicate")
            else:
                if v != expected:
                    raise AssertionError(f"Query param '{name}' expected '{expected}', got '{v}'")

    def handle_request(self, method, path, headers=None, body=None):
        req = Request(method, path, headers or {}, body)
        # CORS preflight
        if req.method == 'OPTIONS' and self._cors:
            return Response(status_code=200, headers=self._cors.copy(), body=b'')
        # Find endpoint
        for ep in self._endpoints:
            if ep['method'] == req.method:
                pat = ep['path']
                if (isinstance(pat, re.Pattern) and pat.match(req.path)) or (pat == req.path):
                    # Rate limiting
                    rl = self._rate_limits.get((ep['method'], pat))
                    if rl:
                        now = time.time()
                        window = rl['window']
                        rl['calls'] = [t for t in rl['calls'] if now - t < window]
                        if len(rl['calls']) >= rl['limit']:
                            retry = int(window - (now - rl['calls'][0])) + 1
                            return Response(status_code=429, headers={'Retry-After': str(retry)}, body=b'')
                        rl['calls'].append(now)
                    # Auth
                    if self._auth:
                        auth = self._auth
                        ah = req.headers.get('Authorization', '')
                        if not ah.lower().startswith(auth['scheme'] + ' '):
                            return Response(status_code=401, headers={'WWW-Authenticate': auth['scheme']}, body=b'')
                        token = ah[len(auth['scheme'])+1:]
                        if not auth['validator'](token):
                            return Response(status_code=403, body=b'Forbidden')
                    # Call handler
                    resp = ep['handler'](req)
                    # apply CORS headers
                    if self._cors and req.method != 'OPTIONS':
                        resp.headers.update(self._cors)
                    return resp
        return Response(status_code=404, body=b'Not Found')

    def mockWebSocket(self, path, handler):
        return self._ws.mockWebSocket(path, handler)

    def ws_connect(self, path):
        return self._ws.connect(path)

class MockWebSocket:
    def __init__(self):
        self._handlers = {}
        self._lock = threading.Lock()

    def mockWebSocket(self, path, handler):
        self._handlers[path] = handler

    def connect(self, path):
        if path not in self._handlers:
            raise ConnectionError("No WebSocket endpoint for path")
        conn = WebSocketConnection()
        thread = threading.Thread(target=self._handlers[path], args=(conn,))
        thread.daemon = True
        thread.start()
        return conn

class WebSocketConnection:
    def __init__(self):
        self._in = []
        self._out = []
        self._cond = threading.Condition()

    def send(self, message):
        # Normalize incoming message for handler (as str)
        if isinstance(message, bytes):
            try:
                message = message.decode()
            except Exception:
                # leave as-is if decode fails
                pass
        with self._cond:
            self._in.append(message)
            self._cond.notify_all()

    def recv(self, timeout=None):
        start = time.time()
        with self._cond:
            while not self._out:
                remaining = None
                if timeout is not None:
                    elapsed = time.time() - start
                    remaining = timeout - elapsed
                    if remaining <= 0:
                        return None
                self._cond.wait(remaining)
            return self._out.pop(0)

    def read(self, timeout=None):
        return self.recv(timeout)

    def write(self, message):
        # Normalize outgoing message to bytes
        if isinstance(message, str):
            message = message.encode()
        with self._cond:
            self._out.append(message)
            self._cond.notify_all()

    def receive_loop(self):
        with self._cond:
            while True:
                while not self._in:
                    self._cond.wait()
                msg = self._in.pop(0)
                return msg
