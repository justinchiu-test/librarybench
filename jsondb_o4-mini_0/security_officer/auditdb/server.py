try:
    from flask import Flask, request, jsonify
    from functools import wraps
except ImportError:
    from functools import wraps

    # Minimal stubs to emulate Flask when it's not installed
    class Args(dict):
        def to_dict(self):
            return dict(self)

    class Request:
        def __init__(self):
            self.method = None
            self.headers = {}
            self.args = Args()
            self._json = None

        def get_json(self):
            return self._json

    request = Request()

    def jsonify(obj):
        return obj

    class Flask:
        def __init__(self, name):
            # routes: mapping (path, method) -> handler
            self._routes = {}

        def route(self, path, methods=None):
            methods = methods or ['GET']
            def decorator(func):
                for m in methods:
                    self._routes[(path, m)] = func
                return func
            return decorator

        def test_client(self):
            return Client(self)

    class Response:
        def __init__(self, data, status_code):
            self._data = data
            self.status_code = status_code

        def get_json(self):
            return self._data

    class Client:
        def __init__(self, app):
            self.app = app

        def open(self, path, method, headers=None, json=None, query_string=None):
            # prepare the stubbed request
            request.method = method
            request.headers = headers or {}
            if method == 'GET':
                request.args = Args(query_string or {})
                request._json = None
            else:
                request.args = Args()
                request._json = json

            handler = self.app._routes.get((path, method))
            if not handler:
                return Response(None, 404)

            result = handler()
            if isinstance(result, Response):
                return result
            if isinstance(result, tuple) and len(result) == 2:
                payload, code = result
            else:
                payload, code = result, 200
            return Response(payload, code)

        def get(self, path, query_string=None, headers=None):
            return self.open(path, 'GET', headers or {}, json=None, query_string=query_string)

        def post(self, path, json=None, headers=None):
            return self.open(path, 'POST', headers or {}, json=json)


def create_app(db):
    app = Flask(__name__)

    def require_role(roles):
        def decorator(f):
            @wraps(f)
            def wrapper(*args, **kwargs):
                role = request.headers.get("Role", "")
                if role not in roles:
                    return jsonify({"error": "Forbidden"}), 403
                return f(role=role, *args, **kwargs)
            return wrapper
        return decorator

    @app.route("/logs", methods=["GET", "POST"])
    def logs():
        if request.method == "GET":
            q = request.args.to_dict()
            results = db.query(q)
            return jsonify(results)
        else:
            role = request.headers.get("Role", "")
            if role not in ("admin", "auditor"):
                return jsonify({"error": "Forbidden"}), 403
            recs = request.get_json()
            try:
                db.batchUpsert(recs)
                return jsonify({"status": "ok"}), 201
            except Exception as e:
                return jsonify({"error": str(e)}), 400

    @app.route("/logs/soft_delete", methods=["POST"])
    @require_role(["admin", "auditor"])
    def soft_delete(role):
        q = request.get_json()
        try:
            db.softDelete(q, role)
            return jsonify({"status": "soft_deleted"}), 200
        except Exception as e:
            return jsonify({"error": str(e)}), 400

    @app.route("/logs/delete", methods=["POST"])
    @require_role(["admin"])
    def hard_delete(role):
        q = request.get_json()
        try:
            db.delete(q, role)
            return jsonify({"status": "deleted"}), 200
        except Exception as e:
            return jsonify({"error": str(e)}), 400

    return app
