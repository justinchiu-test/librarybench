import json

# Minimal request object
class Request:
    def __init__(self):
        self.json = None
        self.data = None
        self.content_type = None

# Global request instance
request = Request()

def jsonify(*args, **kwargs):
    """
    Simple stand-in for Flask's jsonify:
    - if called with one positional argument and no kwargs, return that object
    - if called with multiple args, return them as a list
    - if called with keyword args, return them as a dict
    """
    if args and not kwargs:
        if len(args) == 1:
            return args[0]
        return list(args)
    return kwargs

class Response:
    def __init__(self, body, status_code):
        # body is bytes
        self.data = body
        self.status_code = status_code

    def get_json(self):
        try:
            return json.loads(self.data.decode('utf-8'))
        except Exception:
            return None

class TestClient:
    def __init__(self, app):
        self.app = app

    # support "with app.test_client() as c:"
    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        pass

    def open(self, method, path, data=None, content_type=None):
        # data may be str or bytes
        d = data
        # prepare and dispatch
        return self.app.dispatch_request(method, path, d, content_type)

    def get(self, path):
        return self.open('GET', path)

    def post(self, path, data=None, content_type=None):
        return self.open('POST', path, data, content_type)

    def put(self, path, data=None, content_type=None):
        return self.open('PUT', path, data, content_type)

    def delete(self, path):
        return self.open('DELETE', path, None, None)

class Flask:
    def __init__(self, import_name=None):
        # store (rule, methods, func)
        self.url_map = []

    def route(self, rule, methods=None):
        if methods is None:
            methods = ['GET']
        def decorator(f):
            self.url_map.append((rule, methods, f))
            return f
        return decorator

    def test_client(self):
        return TestClient(self)

    def run(self, *args, **kwargs):
        # no-op in test
        pass

    def dispatch_request(self, method, path, data, content_type):
        # prepare global request
        request.data = data
        request.content_type = content_type
        # parse JSON if applicable
        if content_type and content_type.startswith('application/json') and data:
            try:
                raw = data.decode('utf-8') if isinstance(data, (bytes, bytearray)) else data
                request.json = json.loads(raw)
            except Exception:
                request.json = None
        else:
            request.json = None

        # find matching rule
        for rule, methods, func in self.url_map:
            if method not in methods:
                continue
            rp = rule.strip('/').split('/')
            pp = path.strip('/').split('/')
            if len(rp) != len(pp):
                continue
            args = {}
            matched = True
            for rpart, ppart in zip(rp, pp):
                if rpart.startswith('<') and rpart.endswith('>'):
                    var = rpart[1:-1]
                    args[var] = ppart
                else:
                    if rpart != ppart:
                        matched = False
                        break
            if not matched:
                continue
            # call view
            rv = func(**args)
            # handle return value
            status = 200
            data_out = None
            if isinstance(rv, tuple) and len(rv) == 2:
                data_out, status = rv
            else:
                data_out = rv
            # serialize
            if isinstance(data_out, (dict, list)):
                body = json.dumps(data_out).encode('utf-8')
            elif isinstance(data_out, str):
                body = data_out.encode('utf-8')
            elif data_out is None:
                body = b''
            else:
                # assume bytes
                body = data_out
            return Response(body, status)
        # no route matched
        return Response(b'Not Found', 404)
