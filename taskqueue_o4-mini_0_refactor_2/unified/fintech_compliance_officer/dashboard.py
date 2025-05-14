import json
from fintech_compliance_officer.queue import TaskQueue

# Minimal Flask-like framework for testing without real Flask dependency

class Response:
    def __init__(self, data, status_code=200):
        # Ensure data is text for json.loads compatibility
        if isinstance(data, bytes):
            self.data = data.decode('utf-8')
        else:
            self.data = data
        self.status_code = status_code

class TestClient:
    def __init__(self, app):
        self.app = app

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        pass

    def get(self, path):
        # Dispatch to registered routes
        for rule, func in self.app._routes:
            params = {}
            if self._match(rule, path, params):
                result = func(**params)
                # Unpack result and status
                if isinstance(result, Response):
                    return result
                if isinstance(result, tuple) and len(result) == 2 and isinstance(result[1], int):
                    data_obj, status = result
                else:
                    data_obj, status = result, 200
                # Serialize data_obj if needed
                if isinstance(data_obj, (dict, list)):
                    body = json.dumps(data_obj)
                else:
                    body = data_obj or ''
                return Response(body, status)
        # No matching route
        return Response('', 404)

    def _match(self, rule, path, params):
        # Split and match pattern with possible <var> capture
        rule_parts = rule.strip('/').split('/')
        path_parts = path.strip('/').split('/')
        # Handle root
        if rule_parts == [''] and path_parts == ['']:
            return True
        if len(rule_parts) != len(path_parts):
            return False
        for rp, pp in zip(rule_parts, path_parts):
            if rp.startswith('<') and rp.endswith('>'):
                var = rp[1:-1]
                params[var] = pp
            elif rp != pp:
                return False
        return True

class Flask:
    def __init__(self, name):
        self._routes = []
        self.config = {}

    def route(self, rule):
        def decorator(func):
            self._routes.append((rule, func))
            return func
        return decorator

    def test_client(self):
        return TestClient(self)

def jsonify(data):
    # In view functions we'll return raw data structures;
    # TestClient will JSON-serialize them.
    return data

# Application and queue instance
app = Flask(__name__)
queue = TaskQueue('dash_key')

@app.route('/tasks')
def get_tasks():
    return jsonify(queue.peek_queue())

@app.route('/task/<task_id>')
def get_task(task_id):
    tasks = queue.peek_queue()
    for t in tasks:
        if t['id'] == task_id:
            return jsonify(t)
    # Not found
    return '', 404

@app.route('/metrics')
def get_metrics():
    return jsonify(queue.get_metrics())

@app.route('/deadletters')
def get_dead_letters():
    return jsonify(queue.get_dead_letter_queue())
