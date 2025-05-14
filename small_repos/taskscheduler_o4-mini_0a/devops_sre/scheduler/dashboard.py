import json
from threading import Lock

# Data storage and synchronization
_data_lock = Lock()
_upcoming = []
_history = []
_retries = []

def add_upcoming(job):
    """Add a job to the upcoming list."""
    with _data_lock:
        _upcoming.append(job)

def add_history(job):
    """Add a job to the history list."""
    with _data_lock:
        _history.append(job)

def add_retry(job):
    """Add a job to the retries list."""
    with _data_lock:
        _retries.append(job)

# Response and testing client infrastructure
class Response:
    def __init__(self, status_code, data=b'', json_data=None):
        self.status_code = status_code
        self.data = data
        self._json = json_data

    def get_json(self):
        return self._json

class TestClient:
    def __init__(self, app):
        self.app = app

    def get(self, path):
        handler = self.app._routes.get(('GET', path))
        if handler is None:
            return Response(404, b'Not Found', None)
        result = handler()
        # Handler may return body or (body, status)
        if isinstance(result, tuple) and len(result) == 2:
            body, status = result
        else:
            body, status = result, 200

        # Prepare data bytes and optional json payload
        if isinstance(body, (list, dict)):
            data = json.dumps(body).encode()
            json_payload = body
        elif isinstance(body, str):
            data = body.encode()
            json_payload = None
        elif isinstance(body, bytes):
            data = body
            json_payload = None
        else:
            # Fallback to string representation
            text = str(body)
            data = text.encode()
            json_payload = None

        return Response(status, data, json_payload)

class App:
    def __init__(self):
        self.testing = False
        # Map of (method, path) -> handler
        self._routes = {}

    def route(self, path, methods):
        def decorator(func):
            for m in methods:
                self._routes[(m.upper(), path)] = func
            return func
        return decorator

    def test_client(self):
        return TestClient(self)

# Instantiate our app
app = App()

# Define routes
@app.route('/jobs', methods=['GET'])
def get_jobs():
    with _data_lock:
        data = list(_upcoming)
    return data, 200

@app.route('/history', methods=['GET'])
def get_history():
    with _data_lock:
        data = list(_history)
    return data, 200

@app.route('/retries', methods=['GET'])
def get_retries():
    with _data_lock:
        data = list(_retries)
    return data, 200

@app.route('/health', methods=['GET'])
def health():
    # Return raw string and status code
    return 'ok', 200
