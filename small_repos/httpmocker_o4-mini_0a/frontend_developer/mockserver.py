import re
import time
import threading
import json
import base64

class Request:
    def __init__(self, method, path, headers, body, queryParams):
        self.method = method
        self.path = path
        self.headers = headers or {}
        self.body = body
        self.queryParams = queryParams or {}

class Response:
    def __init__(self, status_code, headers=None, body=None, chunks=None):
        self.status_code = status_code
        self.headers = headers or {}
        self.body = body
        self.chunks = chunks

class MockWebSocketClient:
    def __init__(self):
        self.inbox = []
        self.outbox = []
        self.lock = threading.Lock()

    def send(self, msg):
        with self.lock:
            self.outbox.append(msg)

    def receive(self, timeout=1):
        start = time.time()
        while time.time() - start < timeout:
            with self.lock:
                if self.inbox:
                    return self.inbox.pop(0)
            time.sleep(0.01)
        raise TimeoutError("No message received")

class MockServer:
    def __init__(self):
        self.handlers = {}
        self.cors = {}
        self.auth_rules = []
        self.rate_limits = {}
        self.ws_handlers = {}

    def registerEndpoint(self, method, path, handler):
        method = method.upper()
        self.handlers.setdefault(method, [])
        # remove any existing for same literal path
        self.handlers[method] = [
            (p,h) for (p,h) in self.handlers[method] if p != path
        ]
        self.handlers[method].append((path, handler))

    def configureCORS(self, path, origins='*', headers=None):
        self.cors[path] = {
            'origins': origins,
            'headers': {
                'Access-Control-Allow-Origin': origins,
                'Access-Control-Allow-Headers': ','.join(headers or [])
            }
        }

    def simulateAuth(self, method, path, scheme, verifier):
        self.auth_rules.append((method.upper(), path, scheme, verifier))

    def simulateRateLimiting(self, method, path, limit, window):
        self.rate_limits[(method.upper(), path)] = {
            'limit': limit,
            'remaining': limit,
            'window': window,
            'reset_time': time.time() + window
        }

    def mockWebSocket(self, path, handler):
        self.ws_handlers[path] = handler

    def connect_websocket(self, path):
        if path not in self.ws_handlers:
            raise ValueError("No WebSocket endpoint")
        client = MockWebSocketClient()
        threading.Thread(target=self.ws_handlers[path], args=(client,), daemon=True).start()
        return client

    def handle_request(self, method, path, headers=None, body=None):
        method = method.upper()
        headers = headers or {}
        # CORS preflight
        if method == 'OPTIONS':
            if path in self.cors:
                cfg = self.cors[path]
                return Response(204, headers=cfg['headers'], body=None)
            return Response(404, {}, 'Not Found')

        # Find handler
        handler = None
        for (p,h) in self.handlers.get(method, []):
            if self._match_path(p, path):
                handler = h
                break
        if not handler:
            return Response(404, {}, 'Not Found')

        # Auth
        for (m,p,scheme,verifier) in self.auth_rules:
            if m == method and self._match_path(p, path):
                auth_header = headers.get('Authorization', '')
                if not self._check_auth(auth_header, scheme, verifier):
                    return Response(401, headers={'WWW-Authenticate': scheme}, body='Unauthorized')

        # Rate limiting
        for (m,p), rl in self.rate_limits.items():
            if m == method and self._match_path(p, path):
                now = time.time()
                if now >= rl['reset_time']:
                    rl['remaining'] = rl['limit']
                    rl['reset_time'] = now + rl['window']
                if rl['remaining'] <= 0:
                    retry = int(rl['reset_time'] - now)
                    return Response(429, headers={'Retry-After': str(retry)}, body='Too Many Requests')
                rl['remaining'] -= 1

        # Build request
        req = Request(method, path, headers, body, self._parse_query(path))

        # Call handler
        result = handler(req)
        if isinstance(result, Response):
            return result
        elif isinstance(result, list):
            return Response(200, headers={}, body=None, chunks=result)
        elif isinstance(result, str):
            return Response(200, headers={}, body=result)
        else:
            return Response(200, headers={'Content-Type':'application/json'}, body=json.dumps(result))

    def _match_path(self, p, path):
        if isinstance(p, re.Pattern):
            return bool(p.fullmatch(path))
        return p == path

    def _parse_query(self, path):
        """
        Parses the query string part of a path.
        - For parts of form key=value, maps key to value.
        - For parts without '=', treats the string as a sequence of single-character keys,
          assigning each character its 1-based position in the string as its value.
        """
        if '?' in path:
            q = path.split('?', 1)[1]
            params = {}
            for part in q.split('&'):
                if '=' in part:
                    k, v = part.split('=', 1)
                    params[k] = v
                elif part:
                    # treat each char in part as key, value = position index + 1
                    for idx, ch in enumerate(part):
                        params[ch] = str(idx + 1)
            return params
        return {}

    def _check_auth(self, auth_header, scheme, verifier):
        if not auth_header.startswith(scheme):
            return False
        token = auth_header[len(scheme):].strip()
        return verifier(token)

    @staticmethod
    def assertHeader(req, name, expected):
        val = req.headers.get(name)
        if val is None:
            raise AssertionError(f"Header {name} missing")
        if callable(expected):
            if not expected(val):
                raise AssertionError(f"Header {name} value {val} does not match predicate")
        elif hasattr(expected, 'pattern'):
            if not expected.match(val):
                raise AssertionError(f"Header {name} value {val} does not match pattern")
        else:
            if val != expected:
                raise AssertionError(f"Header {name} value {val} != expected {expected}")

    @staticmethod
    def assertQueryParam(req, name, expected):
        val = req.queryParams.get(name)
        if val is None:
            raise AssertionError(f"Query param {name} missing")
        if callable(expected):
            if not expected(val):
                raise AssertionError(f"Query param {name} value {val} does not match predicate")
        elif hasattr(expected, 'pattern'):
            if not expected.match(val):
                raise AssertionError(f"Query param {name} value {val} does not match pattern")
        else:
            if val != expected:
                raise AssertionError(f"Query param {name} value {val} != expected {expected}")

    @staticmethod
    def assertBody(req, schema_or_func):
        body = req.body
        data = body
        if isinstance(body, str):
            try:
                data = json.loads(body)
            except:
                pass
        if callable(schema_or_func) and not isinstance(schema_or_func, dict):
            if not schema_or_func(data):
                raise AssertionError("Body predicate failed")
        else:
            if not isinstance(data, dict):
                raise AssertionError("Body is not JSON object")
            for k, typ in schema_or_func.items():
                if k not in data or not isinstance(data[k], typ):
                    raise AssertionError(f"Body field {k} missing or not {typ}")
