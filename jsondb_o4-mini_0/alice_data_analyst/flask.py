import json
from urllib.parse import parse_qs, urlparse

class HTTPException(Exception):
    def __init__(self, code):
        self.code = code

def abort(code):
    raise HTTPException(code)

class Request:
    def __init__(self):
        self.json_data = None
        self.args = {}

    def get_json(self):
        return self.json_data

request = Request()

class Response:
    def __init__(self, data, status=200, headers=None):
        self.status_code = status
        self.headers = headers or {}
        if isinstance(data, (dict, list)):
            self._json = data
            self.data = json.dumps(data).encode()
        elif isinstance(data, str):
            self._json = None
            self.data = data.encode()
        elif isinstance(data, bytes):
            self._json = None
            self.data = data
        else:
            self._json = None
            self.data = str(data).encode()

    def get_json(self):
        if self._json is not None:
            return self._json
        try:
            return json.loads(self.data.decode())
        except Exception:
            return None

    def get_data(self, as_text=False):
        if as_text:
            return self.data.decode()
        return self.data

def jsonify(obj):
    return Response(obj, status=200, headers={'Content-Type': 'application/json'})

class Flask:
    def __init__(self, name):
        self.url_map = {}         # method -> [ (parsed_rule, view) ]
        self.before_funcs = []
        self.config = {}

    def before_request(self, fn):
        self.before_funcs.append(fn)

    def route(self, rule, methods=None):
        if methods is None:
            methods = ['GET']
        def decorator(fn):
            parsed = self._parse_rule(rule)
            for m in methods:
                self.url_map.setdefault(m, []).append((parsed, fn))
            return fn
        return decorator

    def _parse_rule(self, rule):
        parts = rule.strip('/').split('/') if rule.strip('/') else []
        out = []
        for p in parts:
            if p.startswith('<') and p.endswith('>'):
                inside = p[1:-1]
                if inside.startswith('int:'):
                    out.append(('int', inside.split(':',1)[1]))
                else:
                    out.append(('str', inside))
            else:
                out.append(('lit', p))
        return out

    def test_client(self):
        return TestClient(self)

    def dispatch(self, method, full_path, json_data=None):
        # prepare request
        pr = urlparse(full_path)
        path = pr.path
        qs = parse_qs(pr.query)
        request.args = {k: v[0] for k, v in qs.items()}
        request.json_data = json_data
        # before_request hooks
        for fn in self.before_funcs:
            fn()
        # find a matching route
        routes = self.url_map.get(method, [])
        parts = path.strip('/').split('/') if path.strip('/') else []
        for pattern, view in routes:
            if len(pattern) != len(parts):
                continue
            kwargs = {}
            ok = True
            for pat, part in zip(pattern, parts):
                kind, name = pat
                if kind == 'lit':
                    if name != part:
                        ok = False; break
                elif kind == 'str':
                    kwargs[name] = part
                elif kind == 'int':
                    try:
                        kwargs[name] = int(part)
                    except:
                        ok = False; break
            if not ok:
                continue
            try:
                result = view(**kwargs)
            except HTTPException as e:
                return Response('', status=e.code)
            return self._make_response(result)
        # no route
        return Response('', status=404)

    def _make_response(self, result):
        if isinstance(result, Response):
            return result
        headers = {}
        if isinstance(result, tuple):
            if len(result) == 3:
                body, status, headers = result
            elif len(result) == 2:
                body, status = result
            else:
                body = result
                status = 200
        else:
            body = result
            status = 200

        if isinstance(body, (dict, list)):
            resp = jsonify(body)
            resp.status_code = status
            resp.headers.update(headers)
            return resp
        else:
            resp = Response(body, status=status, headers=headers)
            return resp

class TestClient:
    def __init__(self, app):
        self.app = app

    # support 'with' context manager
    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        pass

    def get(self, path):
        return self.app.dispatch('GET', path)

    def post(self, path, json=None):
        return self.app.dispatch('POST', path, json)

    def put(self, path, json=None):
        return self.app.dispatch('PUT', path, json)

    def delete(self, path):
        return self.app.dispatch('DELETE', path)
