"""
Minimal Flask-like stub to support watcher.api without external dependency.
"""

# Global request object
class Request:
    def __init__(self):
        self.json = None
        self.args = {}

request = Request()

class Response:
    def __init__(self, data, status=200):
        # data should be a Python object (dict, list, etc.)
        self._data = data
        self.status_code = status

    def get_json(self):
        return self._data

def jsonify(obj):
    return Response(obj, status=200)

class Flask:
    def __init__(self, import_name):
        # routes: key = (path, method) -> view function
        self._routes = {}
        self.config = {}

    def route(self, rule, methods=None):
        if methods is None:
            methods = ['GET']
        def decorator(func):
            for m in methods:
                self._routes[(rule, m.upper())] = func
            return func
        return decorator

    def test_client(self):
        return TestClient(self)

    def handle_request(self, method, path, json=None, args=None):
        key = (path, method.upper())
        view = self._routes.get(key)
        if view is None:
            return Response({"error": "Not Found"}, status=404)
        # populate global request
        request.json = json
        request.args = args or {}
        rv = view()
        # Handle tuple (Response, status)
        if isinstance(rv, tuple) and len(rv) == 2:
            resp, status = rv
            if isinstance(resp, Response):
                resp.status_code = status
                return resp
            else:
                return Response(resp, status=status)
        # Already a Response
        if isinstance(rv, Response):
            return rv
        # Otherwise wrap raw dict/list
        return Response(rv, status=200)

class TestClient:
    def __init__(self, app):
        self.app = app

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        pass

    def post(self, path, json=None):
        return self.app.handle_request('POST', path, json=json)

    def get(self, path, query_string=None):
        return self.app.handle_request('GET', path, args=query_string)
