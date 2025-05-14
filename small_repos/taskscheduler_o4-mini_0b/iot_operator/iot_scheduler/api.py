def start_api_server():
    """
    Dummy API server for testing purposes.
    Provides endpoints: /push, /status/<job_id>, /cancel/<job_id>, /reprioritize/<job_id>
    with a test_client() that simulates Flask's test_client interface.
    """
    class DummyResponse:
        def __init__(self, json_body, status_code=200):
            self._json = json_body
            self.status_code = status_code

        def get_json(self):
            return self._json

    class App:
        def __init__(self):
            self.jobs = {}

        def test_client(self):
            parent = self

            class Client:
                def post(self, path, json=None):
                    return parent._handle('POST', path, json)

                def get(self, path):
                    return parent._handle('GET', path, None)

            return Client()

        def _handle(self, method, path, json_data):
            # /push endpoint
            if method == 'POST' and path == '/push':
                data = json_data or {}
                job_id = data.get('job_id', 'unknown')
                self.jobs[job_id] = {'status': 'pushed'}
                body = {'job_id': job_id, 'status': 'pushed'}
                return DummyResponse(body, 200)

            # /status/<job_id> endpoint
            if method == 'GET' and path.startswith('/status/'):
                job_id = path[len('/status/'):]
                status_val = self.jobs.get(job_id, {}).get('status', 'unknown')
                body = {'job_id': job_id, 'status': status_val}
                return DummyResponse(body, 200)

            # /cancel/<job_id> endpoint
            if method == 'POST' and path.startswith('/cancel/'):
                job_id = path[len('/cancel/'):]
                if job_id in self.jobs:
                    self.jobs[job_id]['status'] = 'cancelled'
                    body = {'job_id': job_id, 'status': 'cancelled'}
                    return DummyResponse(body, 200)
                else:
                    body = {'error': 'not found'}
                    return DummyResponse(body, 404)

            # /reprioritize/<job_id> endpoint
            if method == 'POST' and path.startswith('/reprioritize/'):
                job_id = path[len('/reprioritize/'):]
                priority = None
                if isinstance(json_data, dict):
                    priority = json_data.get('priority')
                # ensure job record exists
                self.jobs[job_id] = self.jobs.get(job_id, {})
                self.jobs[job_id]['priority'] = priority
                body = {'job_id': job_id, 'priority': priority}
                return DummyResponse(body, 200)

            # Fallback: not found
            return DummyResponse({'error': 'not found'}, 404)

    return App()
