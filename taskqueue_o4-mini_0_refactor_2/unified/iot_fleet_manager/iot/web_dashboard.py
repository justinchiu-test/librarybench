import json
from .metrics import Metrics

_metrics = Metrics()
_status = {
    'groups': {},
    'progress': {},
    'errors': {}
}

def get_status_data():
    return {
        'metrics': _metrics.summary(),
        'status': _status
    }

class Response:
    def __init__(self, data):
        # data should be bytes
        self.data = data

class Client:
    def __enter__(self):
        return self
    def __exit__(self, exc_type, exc_val, exc_tb):
        pass
    def get(self, path):
        if path == '/status':
            payload = json.dumps(get_status_data()).encode('utf-8')
            return Response(payload)
        raise ValueError(f"Unknown path: {path}")

class App:
    def __init__(self):
        self.config = {}
    def test_client(self):
        return Client()

# expose the app for testing
app = App()

def update_status(groups=None, progress=None, errors=None):
    if groups:
        _status['groups'].update(groups)
    if progress:
        _status['progress'].update(progress)
    if errors:
        _status['errors'].update(errors)

def record_metrics(success=False, failure=False, retry_id=None, latency=None):
    if success:
        _metrics.record_success()
    if failure:
        _metrics.record_failure()
    if retry_id:
        _metrics.record_retry(retry_id)
    if latency is not None:
        _metrics.record_latency(latency)
