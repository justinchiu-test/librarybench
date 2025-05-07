# Stub implementation of Flask for unified tests
import json as _json

class Response:
    def __init__(self, data, status_code):
        self._data = data
        self.status_code = status_code
    def get_json(self):
        return self._data
    @property
    def data(self):
        return _json.dumps(self._data)

class Request:
    def __init__(self):
        self._json = None
    def get_json(self):
        return self._json
request = Request()

class Flask:
    def __init__(self, name):
        self._rules = []  # list of (rule, methods, function)
        self.testing = False
        self.config = {}
    def route(self, rule, methods=None):
        if methods is None:
            methods = ['GET']
        def decorator(fn):
            self._rules.append((rule, methods, fn))
            return fn
        return decorator
    def test_client(self):
        return TestClient(self)

class TestClient:
    def __init__(self, app):
        self.app = app
    def __enter__(self):
        return self
    def __exit__(self, exc_type, exc, tb):
        return False
    def open(self, path, method, json=None):
        for rule, methods, fn in self.app._rules:
            if method in methods and self._match_rule(rule, path):
                request._json = json
                rv = fn(**self._extract_args(rule, path))
                if isinstance(rv, tuple):
                    data, code = rv
                else:
                    data, code = rv, 200
                return Response(data, code)
        return Response({'error': 'Not found'}, 404)
    def post(self, path, json=None):
        return self.open(path, 'POST', json)
    def get(self, path):
        return self.open(path, 'GET', None)
    def _extract_args(self, rule, path):
        args = {}
        r_parts = rule.strip('/').split('/')
        p_parts = path.strip('/').split('/')
        for r, p in zip(r_parts, p_parts):
            if r.startswith('<') and r.endswith('>'):
                inside = r[1:-1]
                if ':' in inside:
                    typ, name = inside.split(':', 1)
                    if typ == 'int':
                        args[name] = int(p)
                    else:
                        args[name] = p
                else:
                    args[inside] = p
        return args
    def _match_rule(self, rule, path):
        # match rule patterns with parameters
        r_parts = rule.strip('/').split('/')
        p_parts = path.strip('/').split('/')
        if len(r_parts) != len(p_parts):
            return False
        for r, p in zip(r_parts, p_parts):
            if r.startswith('<') and r.endswith('>'):
                continue
            if r != p:
                return False
        return True

def jsonify(*args, **kwargs):
    if args:
        return args[0]
    return kwargs