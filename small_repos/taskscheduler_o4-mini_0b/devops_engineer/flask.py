import json

class Request:
    def __init__(self):
        self.json = None

    def get_json(self):
        return self.json

# singleton request object
request = Request()

class Response:
    def __init__(self, body, status_code):
        # body is expected to be serializable to JSON
        self._json = body
        self.status_code = status_code
        try:
            self.data = json.dumps(body)
        except Exception:
            # fallback to string
            self.data = str(body)

    def get_json(self):
        return self._json

class Flask:
    def __init__(self, name):
        self.name = name
        # map of (route, method) to view function
        self.url_map = {}

    def add_url_rule(self, rule, endpoint=None, view_func=None, methods=None):
        methods = methods or []
        for method in methods:
            self.url_map[(rule, method)] = view_func

    def test_client(self):
        return TestClient(self)

class TestClient:
    def __init__(self, app):
        self.app = app

    def open(self, path, method, data=None, content_type=None):
        # prepare the fake request
        # set the global request.json based on data and content_type
        if content_type and 'application/json' in content_type and data:
            try:
                request.json = json.loads(data)
            except Exception:
                request.json = None
        else:
            request.json = None

        # lookup the view function
        view = self.app.url_map.get((path, method))
        if not view:
            return Response({'error': 'Not Found'}, 404)

        # call the view
        rv = view()
        # view returns either (body, status) or just body
        if isinstance(rv, tuple) and len(rv) == 2:
            body, status = rv
        else:
            body, status = rv, 200
        return Response(body, status)

    def post(self, path, data=None, content_type=None):
        return self.open(path, 'POST', data=data, content_type=content_type)

    def get(self, path):
        return self.open(path, 'GET')
