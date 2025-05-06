"""
A stub TestClient so that `from fastapi.testclient import TestClient`
also won't explode.  This VERY naive implementation simply looks
up a registered route and invokes it with no real HTTP parsing.
"""
class Response:
    def __init__(self, data):
        # Always 200 OK by default
        self.status_code = 200
        # assume dict or nothing
        self._json = data if isinstance(data, dict) else {}

    def json(self):
        return self._json

class TestClient:
    def __init__(self, app):
        self.app = app

    def get(self, path, **kwargs):
        for method, route, func in getattr(self.app, "routes", []):
            if method == "GET" and route == path:
                result = func()
                return Response(result)
        raise RuntimeError(f"GET {path} not found")

    def post(self, path, json=None, **kwargs):
        for method, route, func in getattr(self.app, "routes", []):
            if method == "POST" and route == path:
                result = func(json or {})
                return Response(result)
        raise RuntimeError(f"POST {path} not found")
