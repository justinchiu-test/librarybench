import pytest
import json
from api import app, scheduler

@pytest.fixture(scope='module')
def client():
    with app.test_client() as c:
        yield c

def test_list_empty(client):
    rv = client.get('/jobs')
    assert rv.status_code == 200
    assert rv.get_json() == []

def test_create_interval_job(client):
    payload = {'type': 'interval', 'interval': 5, 'func': 'noop'}
    rv = client.post('/jobs', data=json.dumps(payload), content_type='application/json')
    assert rv.status_code == 201
    data = rv.get_json()
    job_id = data['job_id']
    # Get job
    rv2 = client.get(f'/jobs/{job_id}')
    assert rv2.status_code == 200
    info = rv2.get_json()
    assert info['schedule_type'] == 'interval'
    # Delete job
    rv3 = client.delete(f'/jobs/{job_id}')
    assert rv3.status_code == 200
    rv4 = client.get('/jobs')
    assert all(j['job_id'] != job_id for j in rv4.get_json())

def test_reschedule_api(client):
    payload = {'type': 'interval', 'interval': 3, 'func': 'noop'}
    rv = client.post('/jobs', data=json.dumps(payload), content_type='application/json')
    job_id = rv.get_json()['job_id']
    rv2 = client.put(f'/jobs/{job_id}', data=json.dumps({'interval': 7}), content_type='application/json')
    assert rv2.status_code == 200
    info = client.get(f'/jobs/{job_id}').get_json()
    assert info['schedule_params']['interval'] == 7
    client.delete(f'/jobs/{job_id}')

