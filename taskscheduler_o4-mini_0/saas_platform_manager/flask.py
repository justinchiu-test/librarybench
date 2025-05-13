import re
import threading
import json

# A real Flask request context is threaded; we simulate that.
_request_ctx = threading.local()

class Request:
    def __init__(self, data=None, content_type=None):
        # store raw bytes
        self._data = data or b''
        self.content_type = content_type

    def get_json(self):
        if not self._data:
            return None
        # decode bytes to string if needed
        if isinstance(self._data, (bytes, bytearray)):
            text = self._data.decode('utf-8')
        else:
            text = self._data
        return json.loads(text)

class RequestProxy:
    # proxy to the real request on the thread-local
    def get_json(self):
        req = getattr(_request_ctx, 'request', None)
        if req is None:
            return None
        return req.get_json()

# this is what handlers will see as "request"
request = RequestProxy()

def jsonify(obj):
    # return a JSON string (the api_server assumes it returns something JSON-able)
    return json.dumps(obj)

class Response:
    def __init__(self, status_code, data):
        self.status_code = status_code
        # ensure bytes
        if isinstance(data, (bytes, bytearray)):
            self.data = data
        elif isinstance(data, str):
            self.data = data.encode('utf-8')
        else:
            # fallback: dump JSON
            self.data = json.dumps(data).encode('utf-8')

    def get_json(self):
        if not self.data:
            return None
        return json.loads(self.data.decode('utf-8'))

class TestClient:
    def __init__(self, app):
        self.app = app

    def get(self, path):
        return self.open('GET', path)

    def post(self, path, data=None, content_type=None):
        raw = data
        if isinstance(data, str):
            raw = data.encode('utf-8')
        return self.open('POST', path, raw, content_type)

    def delete(self, path):
        return self.open('DELETE', path)

    def open(self, method, path, data=None, content_type=None):
        return self.app._handle_request(method, path, data, content_type)

class Flask:
    def __init__(self, name):
        # list of (compiled_regex, set_of_methods, handler)
        self.url_map = []
        self.config = {}

    def route(self, rule, methods):
        # convert "/foo/<bar>/baz" into regex with named group 'bar'
        pattern = '^' + re.sub(r'<([^>]+)>', r'(?P<\1>[^/]+)', rule) + '$'
        regex = re.compile(pattern)

        def decorator(f):
            self.url_map.append((regex, set(methods), f))
            return f
        return decorator

    def test_client(self):
        return TestClient(self)

    def run(self, port):
        raise NotImplementedError("Standalone server not implemented in tests")

    def _handle_request(self, method, path, data=None, content_type=None):
        # iterate routes for a match
        for regex, methods, handler in self.url_map:
            m = regex.match(path)
            if m and method in methods:
                # bind a new Request into thread-local
                req = Request(data=data, content_type=content_type)
                _request_ctx.request = req
                # call handler with path params
                rv = handler(**m.groupdict())
                # handler may return (body, status) or just body
                if isinstance(rv, tuple):
                    body, status = rv
                else:
                    body, status = rv, 200
                # ensure bytes body
                if isinstance(body, str):
                    resp_body = body.encode('utf-8')
                else:
                    resp_body = body
                return Response(status, resp_body)
        # no matching route
        return Response(404, b'')
