import time
import pytest
from unified.pm.api import app, manager

@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client
    # cleanup
    manager.shutdown()

def test_api_create_and_get_task(client):
    # create a simple add task
    resp = client.post('/tasks', json={'task_name': 'add', 'args': [2, 3]})
    assert resp.status_code == 202
    tid = resp.get_json()['task_id']
    # wait for completion
    time.sleep(0.1)
    resp2 = client.get(f'/tasks/{tid}')
    assert resp2.status_code == 200
    meta = resp2.get_json()
    assert meta['status'] == 'success'

def test_api_cancel_task(client):
    resp = client.post('/tasks', json={'task_name': 'sleep', 'args': [0.5]})
    assert resp.status_code == 202
    tid = resp.get_json()['task_id']
    time.sleep(0.1)
    resp2 = client.post(f'/tasks/{tid}/cancel')
    assert resp2.status_code == 200
    # check status
    time.sleep(0.1)
    resp3 = client.get(f'/tasks/{tid}')
    assert resp3.get_json()['status'] == 'canceled'

def test_api_set_timeout(client):
    resp = client.post('/tasks', json={'task_name': 'sleep', 'args': [0.5], 'timeout':1})
    tid = resp.get_json()['task_id']
    # update timeout to very small
    resp2 = client.post(f'/tasks/{tid}/timeout', json={'timeout': 0.1})
    assert resp2.status_code == 200
    time.sleep(0.2)
    resp3 = client.get(f'/tasks/{tid}')
    assert resp3.get_json()['status'] == 'timeout'