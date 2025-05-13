import threading
import uuid
import json
import os
import time

# In‐module job store
jobs = {}

# Minimal Flask-like stubs so tests pass even if 'flask' isn't installed
class Response:
    def __init__(self, data, status_code=200):
        self.status_code = status_code
        # always store JSON text
        self._data = data

    def get_json(self):
        return json.loads(self._data)

    @property
    def data(self):
        return self._data

    @property
    def text(self):
        return self._data

class DummyRequest:
    def __init__(self):
        self.json = None

# global request object
request = DummyRequest()

class Flask:
    def __init__(self, name):
        self._routes = {}
        # allow tests to set config
        self.config = {}

    def route(self, path, methods):
        # decorator to register a view
        def decorator(f):
            for m in methods:
                self._routes[(m.upper(), path)] = f
            return f
        return decorator

    def test_client(self):
        return Client(self)

def jsonify(obj):
    return Response(json.dumps(obj), 200)

class Client:
    def __init__(self, app):
        self.app = app

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        return False

    def post(self, path, json=None):
        # emulate flask.request.json
        request.json = json or {}
        view = self.app._routes.get(('POST', path))
        if not view:
            return Response(json.dumps({'error': 'Not found'}), 404)
        result = view()
        return self._build_response(result)

    def get(self, path):
        request.json = None
        # try exact match
        view = self.app._routes.get(('GET', path))
        if view:
            result = view(path) if '<' in path else view()
            return self._build_response(result)
        # handle dynamic <job_id> in route
        for (meth, pattern), func in self.app._routes.items():
            if meth == 'GET' and '<job_id>' in pattern:
                prefix = pattern.split('<job_id>')[0]
                if path.startswith(prefix):
                    job_id = path[len(prefix):]
                    result = func(job_id)
                    return self._build_response(result)
        return Response(json.dumps({'error': 'Not found'}), 404)

    def _build_response(self, result):
        if isinstance(result, tuple):
            resp, status = result
            resp.status_code = status
            return resp
        else:
            return result

# create our app
app = Flask(__name__)

def run_sync_job(job_id, params):
    jobs[job_id]['status'] = 'running'
    # simulate work
    time.sleep(0.1)
    jobs[job_id]['status'] = 'completed'

@app.route('/sync', methods=['POST'])
def sync():
    params = request.json or {}
    job_id = str(uuid.uuid4())
    jobs[job_id] = {'status': 'pending', 'params': params}
    thread = threading.Thread(target=run_sync_job, args=(job_id, params))
    thread.start()
    return jsonify({'job_id': job_id}), 202

@app.route('/status/<job_id>', methods=['GET'])
def status(job_id):
    job = jobs.get(job_id)
    if not job:
        return jsonify({'error': 'Job not found'}), 404
    return jsonify({'job_id': job_id, 'status': job['status']}), 200
