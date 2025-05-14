import json
import pytest
from iot_scheduler.api import start_api_server

@pytest.fixture
def client():
    app = start_api_server()
    return app.test_client()

def test_push_and_status_and_cancel(client):
    resp = client.post('/push', json={'job_id': 'job1'})
    assert resp.status_code == 200
    data = resp.get_json()
    assert data['status'] == 'pushed'
    resp = client.get('/status/job1')
    assert resp.get_json()['status'] == 'pushed'
    resp = client.post('/cancel/job1')
    assert resp.get_json()['status'] == 'cancelled'
    resp = client.get('/status/job1')
    assert resp.get_json()['status'] == 'cancelled'

def test_reprioritize(client):
    resp = client.post('/reprioritize/job2', json={'priority': 5})
    assert resp.status_code == 200
    assert resp.get_json()['priority'] == 5
