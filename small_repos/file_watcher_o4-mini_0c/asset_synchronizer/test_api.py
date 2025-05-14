import pytest
from sync_tool.api import app, jobs

@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

def test_sync_endpoint(client):
    resp = client.post('/sync', json={'param':'value'})
    assert resp.status_code == 202
    data = resp.get_json()
    assert 'job_id' in data
    job_id = data['job_id']
    assert job_id in jobs

def test_status_endpoint(client):
    resp = client.post('/sync')
    data = resp.get_json()
    job_id = data['job_id']
    resp2 = client.get(f'/status/{job_id}')
    assert resp2.status_code == 200
    data2 = resp2.get_json()
    assert data2['status'] in ['pending','running','completed']
    resp3 = client.get('/status/unknown')
    assert resp3.status_code == 404
