import re
import time
import threading
import json
from collections import deque

# Minimal JSON Schema validation fallback if jsonschema is not installed
class ValidationError(Exception):
    pass

def validate(instance, schema):
    """A minimal JSON Schema validator supporting type, properties, required, items, enum."""
    # Validate type
    stype = schema.get('type')
    if stype:
        if stype == 'object':
            if not isinstance(instance, dict):
                raise ValidationError(f"Expected object, got {type(instance).__name__}")
            # required fields
            for req in schema.get('required', []):
                if req not in instance:
                    raise ValidationError(f"Missing required property: {req}")
            # properties
            for prop, subs in schema.get('properties', {}).items():
                if prop in instance and isinstance(subs, dict):
                    val = instance[prop]
                    ptype = subs.get('type')
                    if ptype:
                        if ptype == 'number':
                            if not isinstance(val, (int, float)):
                                raise ValidationError(f"Property {prop} expected number, got {type(val).__name__}")
                        elif ptype == 'string':
                            if not isinstance(val, str):
                                raise ValidationError(f"Property {prop} expected string, got {type(val).__name__}")
                        elif ptype == 'boolean':
                            if not isinstance(val, bool):
                                raise ValidationError(f"Property {prop} expected boolean, got {type(val).__name__}")
                        elif ptype == 'object':
                            if not isinstance(val, dict):
                                raise ValidationError(f"Property {prop} expected object, got {type(val).__name__}")
                        elif ptype == 'array':
                            if not isinstance(val, list):
                                raise ValidationError(f"Property {prop} expected array, got {type(val).__name__}")
        elif stype == 'array':
            if not isinstance(instance, list):
                raise ValidationError(f"Expected array, got {type(instance).__name__}")
            items = schema.get('items')
            if items:
                for item in instance:
                    validate(item, items)
        elif stype == 'string':
            if not isinstance(instance, str):
                raise ValidationError(f"Expected string, got {type(instance).__name__}")
        elif stype == 'number':
            if not isinstance(instance, (int, float)):
                raise ValidationError(f"Expected number, got {type(instance).__name__}")
        elif stype == 'boolean':
            if not isinstance(instance, bool):
                raise ValidationError(f"Expected boolean, got {type(instance).__name__}")
    # Enum constraint
    if 'enum' in schema:
        if instance not in schema['enum']:
            raise ValidationError(f"Value {instance} not in enum {schema['enum']}")

class MockWebSocketConnection:
    def __init__(self):
        # queue holds messages for this endpoint to recv()
        self.queue = deque()
        # peer is the other end of the connection
        self.peer = None

    def send(self, message):
        # send to peer's queue if linked, otherwise to own queue
        if self.peer:
            self.peer.queue.append(message)
        else:
            self.queue.append(message)

    def recv(self, timeout=None):
        start = time.time()
        while True:
            if self.queue:
                return self.queue.popleft()
            if timeout is not None and (time.time() - start) > timeout:
                raise TimeoutError("WebSocket recv timeout")
            time.sleep(0.01)

class MockServer:
    def __init__(self):
        self.handlers = []
        self.ws_handlers = []

    def registerEndpoint(self, method, path, handler):
        if isinstance(path, re.Pattern):
            pattern = path
        else:
            pattern = re.compile('^' + re.escape(path) + '$')
        h = {
            'method': method.upper(),
            'pattern': pattern,
            'handler': handler,
            'header_assertions': [],
            'body_assertions': [],
            'query_assertions': [],
            'cors': None,
            'auth': None,
            'rate_limit': None,
            'chunked': None,
            'requests': []
        }
        self.handlers.append(h)
        return self

    def assertHeader(self, key, value_or_pattern):
        h = self.handlers[-1]
        h['header_assertions'].append((key, value_or_pattern))
        return self

    def assertBody(self, schema_or_predicate):
        h = self.handlers[-1]
        h['body_assertions'].append(schema_or_predicate)
        return self

    def assertQueryParam(self, key, value_or_pattern):
        h = self.handlers[-1]
        h['query_assertions'].append((key, value_or_pattern))
        return self

    def configureCORS(self, allowed_origins="*", allowed_methods=None, allowed_headers=None):
        h = self.handlers[-1]
        h['cors'] = {
            'origins': allowed_origins,
            'methods': allowed_methods,
            'headers': allowed_headers
        }
        return self

    def simulateAuth(self, auth_type, credentials):
        h = self.handlers[-1]
        h['auth'] = {
            'type': auth_type.lower(),
            'credentials': credentials
        }
        return self

    def simulateRateLimiting(self, limit, window_seconds):
        h = self.handlers[-1]
        h['rate_limit'] = {
            'limit': limit,
            'window': window_seconds
        }
        h['requests'] = []
        return self

    def simulateChunkedTransfer(self, chunks, interval_seconds=0):
        h = self.handlers[-1]
        h['chunked'] = {
            'chunks': chunks,
            'interval': interval_seconds
        }
        return self

    def mockWebSocket(self, path, on_connect):
        if isinstance(path, re.Pattern):
            pattern = path
        else:
            pattern = re.compile('^' + re.escape(path) + '$')
        self.ws_handlers.append((pattern, on_connect))
        return self

    def hotReloadHandlers(self, new_defs):
        self.handlers.clear()
        for method, path, handler in new_defs:
            self.registerEndpoint(method, path, handler)
        return self

    def dispatch_request(self, method, path, headers=None, body=None, query=None):
        headers = headers or {}
        query = query or {}

        # Handle CORS preflight for any matching path (regardless of method)
        if method.upper() == 'OPTIONS':
            for h in self.handlers:
                if h['pattern'].match(path) and h.get('cors'):
                    resp_headers = {
                        'Access-Control-Allow-Origin': h['cors']['origins']
                    }
                    if h['cors']['methods']:
                        resp_headers['Access-Control-Allow-Methods'] = ','.join(h['cors']['methods'])
                    if h['cors']['headers']:
                        resp_headers['Access-Control-Allow-Headers'] = ','.join(h['cors']['headers'])
                    return {'status': 204, 'headers': resp_headers, 'body': None}

        for h in self.handlers:
            if h['method'] == method.upper() and h['pattern'].match(path):
                # CORS preflight (legacy, but method-specific)
                if method.upper() == 'OPTIONS' and h['cors']:
                    resp_headers = {}
                    cfg = h['cors']
                    resp_headers['Access-Control-Allow-Origin'] = cfg['origins']
                    if cfg['methods']:
                        resp_headers['Access-Control-Allow-Methods'] = ','.join(cfg['methods'])
                    if cfg['headers']:
                        resp_headers['Access-Control-Allow-Headers'] = ','.join(cfg['headers'])
                    return {'status': 204, 'headers': resp_headers, 'body': None}

                # Auth
                if h['auth']:
                    auth = h['auth']
                    auth_hdr = headers.get('Authorization')
                    if auth['type'] == 'basic':
                        import base64
                        expected = "Basic " + base64.b64encode(
                            f"{auth['credentials'][0]}:{auth['credentials'][1]}".encode()
                        ).decode()
                        if auth_hdr != expected:
                            return {'status': 401, 'headers': {}, 'body': 'Unauthorized'}
                    elif auth['type'] == 'bearer':
                        expected = f"Bearer {auth['credentials']}"
                        if auth_hdr != expected:
                            return {'status': 401, 'headers': {}, 'body': 'Unauthorized'}

                # Rate limit
                if h['rate_limit']:
                    now = time.time()
                    window = h['rate_limit']['window']
                    reqs = [t for t in h['requests'] if now - t < window]
                    if len(reqs) >= h['rate_limit']['limit']:
                        return {'status': 429, 'headers': {'Retry-After': str(window)}, 'body': 'Too Many Requests'}
                    reqs.append(now)
                    h['requests'] = reqs

                # Header assertions
                for key, val in h['header_assertions']:
                    actual = headers.get(key)
                    if isinstance(val, re.Pattern):
                        if not actual or not val.fullmatch(actual):
                            raise AssertionError(f"Header {key} value {actual} does not match {val.pattern}")
                    else:
                        if actual != val:
                            raise AssertionError(f"Header {key} value {actual} != {val}")

                # Query assertions
                for key, val in h['query_assertions']:
                    actual = query.get(key)
                    if isinstance(val, re.Pattern):
                        if not actual or not val.fullmatch(actual):
                            raise AssertionError(f"Query {key} value {actual} does not match {val.pattern}")
                    else:
                        if actual != val:
                            raise AssertionError(f"Query {key} value {actual} != {val}")

                # Body assertions
                parsed_body = body
                if body and isinstance(body, str):
                    try:
                        parsed_body = json.loads(body)
                    except Exception:
                        parsed_body = body
                for assertion in h['body_assertions']:
                    if isinstance(assertion, dict):
                        try:
                            validate(parsed_body, assertion)
                        except ValidationError as e:
                            raise AssertionError(f"JSON schema validation failed: {e}")
                    else:
                        if not assertion(parsed_body):
                            raise AssertionError("Body predicate failed")

                # Call handler
                result = h['handler']({
                    'method': method,
                    'path': path,
                    'headers': headers,
                    'body': parsed_body,
                    'query': query
                })

                # Build response
                status = 200
                resp_headers = {}
                resp_body = None
                if isinstance(result, tuple):
                    status, resp_headers, resp_body = result
                else:
                    resp_body = result

                # CORS for normal request
                if h['cors']:
                    cfg = h['cors']
                    resp_headers['Access-Control-Allow-Origin'] = cfg['origins']

                # Chunked transfer
                if h['chunked']:
                    def gen():
                        for chunk in h['chunked']['chunks']:
                            yield {'status': status, 'headers': resp_headers, 'body': chunk}
                            if h['chunked']['interval']:
                                time.sleep(h['chunked']['interval'])
                    return gen()

                return {'status': status, 'headers': resp_headers, 'body': resp_body}

        raise ValueError("No matching endpoint")

    def connect_websocket(self, path):
        for pattern, on_connect in self.ws_handlers:
            if pattern.match(path):
                # Create a paired connection for client and server sides
                server_conn = MockWebSocketConnection()
                client_conn = MockWebSocketConnection()
                # Link peers for directional messaging
                server_conn.peer = client_conn
                client_conn.peer = server_conn
                # Start server-side handler
                threading.Thread(target=on_connect, args=(server_conn,), daemon=True).start()
                # Return client-facing connection
                return client_conn
        raise ValueError("No matching WebSocket endpoint")
