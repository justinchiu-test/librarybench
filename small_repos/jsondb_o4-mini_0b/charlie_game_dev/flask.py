from types import SimpleNamespace

# A global request object that handlers will read from
request = SimpleNamespace(json=None)

def jsonify(*args, **kwargs):
    # Return the single positional argument, or kwargs if given.
    if args and not kwargs:
        return args[0] if len(args) == 1 else args
    if kwargs and not args:
        return kwargs
    if args and kwargs:
        return args, kwargs
    return None

class Flask:
    def __init__(self, import_name):
        # route map: keys are (path, method), values are view functions
        self.routes = {}

    def route(self, path, methods=None):
        if methods is None:
            methods = ['GET']
        def decorator(fn):
            for m in methods:
                self.routes[(path, m.upper())] = fn
            return fn
        return decorator

    def test_client(self):
        return Client(self)

class Response:
    def __init__(self, data, status):
        self.status_code = status
        self._data = data

    def get_json(self):
        return self._data

class Client:
    def __init__(self, app):
        self.app = app

    def get(self, path):
        return self._request('GET', path, None)

    def post(self, path, json=None):
        return self._request('POST', path, json)

    def put(self, path, json=None):
        return self._request('PUT', path, json)

    def _request(self, method, path, json_data):
        import flask  # grabs our stub flask.py
        # Inject JSON payload into flask.request
        flask.request.json = json_data
        # Find the registered view
        fn = self.app.routes.get((path, method.upper()))
        if not fn:
            raise RuntimeError(f"No route registered for {method} {path}")
        result = fn()
        # View returns either (body, status) or just body
        if isinstance(result, tuple) and len(result) == 2:
            body, status = result
        else:
            body, status = result, 200
        return Response(body, status)
