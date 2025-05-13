import json
import pytest
from app import app, scheduler

@pytest.fixture
def client():
    return app.test_client()

def test_run_endpoint_success(client):
    # register executor and task
    from scheduler.executors import MultiprocessingExecutor
    scheduler.set_executor(MultiprocessingExecutor(processes=1))
    def task_foo():
        return "bar"
    scheduler.task_foo = task_foo
    resp = client.post('/run', data=json.dumps({'task': 'foo'}), content_type='application/json')
    data = resp.get_json()
    assert resp.status_code == 200
    assert data['status'] == 'success'
    assert data['result'] == 'bar'

def test_run_endpoint_error(client):
    # no such task
    from scheduler.executors import MultiprocessingExecutor
    scheduler.set_executor(MultiprocessingExecutor(processes=1))
    resp = client.post('/run', data=json.dumps({'task': 'no'}), content_type='application/json')
    data = resp.get_json()
    assert resp.status_code == 500
    assert data['status'] == 'error'
    assert 'Task or executor not found' in data['error']
    # alert was sent
    assert scheduler.alerts[-1][0] == 'slack'

def test_logs_and_cancel(client):
    r = client.get('/logs')
    assert r.status_code == 200
    assert 'logs' in r.get_json()
    c = client.post('/cancel')
    assert c.status_code == 200
    assert c.get_json()['status'] == 'cancelled'
    assert scheduler._shutdown.is_set()
