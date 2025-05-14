import pytest
import json
from dashboard import app, queue

@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as c:
        yield c

def test_tasks_endpoint_empty(client):
    rv = client.get('/tasks')
    assert rv.status_code == 200
    data = json.loads(rv.data)
    assert isinstance(data, list)
    assert data == []

def test_dashboard_after_enqueue(client):
    tid = queue.enqueue({'foo': 'bar'})
    rv = client.get('/tasks')
    data = json.loads(rv.data)
    assert any(t['id'] == tid for t in data)
    rv2 = client.get(f'/task/{tid}')
    assert rv2.status_code == 200
    tdata = json.loads(rv2.data)
    assert tdata['id'] == tid

def test_metrics_endpoint(client):
    rv = client.get('/metrics')
    data = json.loads(rv.data)
    assert 'throughput' in data

def test_deadletters_endpoint(client):
    tid = queue.enqueue({'x': 'y'})
    for _ in range(queue.max_retries + 1):
        queue.retry_task(tid)
    rv = client.get('/deadletters')
    data = json.loads(rv.data)
    assert any(t['id'] == tid for t in data)
