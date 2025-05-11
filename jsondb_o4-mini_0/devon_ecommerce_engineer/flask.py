import re
import json

class HTTPException(Exception):
    def __init__(self, code):
        self.code = code

def abort(code):
    raise HTTPException(code)

def jsonify(data):
    return data

class request:
    json = None

class Response:
    def __init__(self, data, status_code):
        self.status_code = status_code
        self._data = data
        # determine JSON payload
        if isinstance(data, (dict, list)):
            self._json = data
        else:
            self._json = None

    def get_json(self):
        return self._json

class Flask:
    def __init__(self, name):
        self.name = name
        # each entry: (methods, compiled_regex, handler)
        self.routes = []

    def route(self, rule, methods=None):
        if methods is None:
            methods = ['GET']
        def decorator(func):
            # Build regex pattern from rule
            # e.g. '/products/<product_id>' -> r'^/products/(?P<product_id>[^/]+)$'
            pattern = ''
            parts = rule.strip('/').split('/')
            for part in parts:
                if part.startswith('<') and part.endswith('>'):
                    name = part[1:-1]
                    pattern += '/(?P<%s>[^/]+)' % name
                else:
                    pattern += '/' + re.escape(part)
            pattern = '^' + pattern + '$'
            compiled = re.compile(pattern)
            self.routes.append((methods, compiled, func))
            return func
        return decorator

    def dispatch_request(self, method, path, json_data=None):
        # set request.json
        request.json = json_data
        # find matching route
        for methods, regex, handler in self.routes:
            if method in methods:
                m = regex.match(path)
                if m:
                    kwargs = m.groupdict()
                    try:
                        result = handler(**kwargs)
                        # handler can return (data, status) or data
                        if isinstance(result, tuple) and len(result) == 2:
                            data, status = result
                        else:
                            data, status = result, None
                        # assign default status if not provided
                        if status is None:
                            if method == 'POST':
                                status = 201
                            elif method == 'DELETE':
                                status = 204
                            else:
                                status = 200
                        return Response(data, status)
                    except HTTPException as e:
                        return Response(None, e.code)
        # no matching route
        return Response(None, 404)

    def test_client(self):
        return TestClient(self)

class TestClient:
    def __init__(self, app):
        self.app = app

    def get(self, path):
        return self.app.dispatch_request('GET', path)

    def post(self, path, json=None):
        return self.app.dispatch_request('POST', path, json)

    def patch(self, path, json=None):
        return self.app.dispatch_request('PATCH', path, json)

    def delete(self, path):
        return self.app.dispatch_request('DELETE', path)
