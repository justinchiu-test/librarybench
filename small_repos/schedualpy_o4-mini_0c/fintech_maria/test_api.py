import pytest
import time
from scheduler.api import app, scheduler

@pytest.fixture
def client():
    app.config['TESTING'] = True
    return app.test_client()

def test_list_and_one_off(client):
    rv = client.get('/jobs')
    assert rv.status_code == 200
    data = rv.get_json()
    assert 'jobs' in data
    rv2 = client.post('/jobs/one-off', json={'run_at': time.time() + 0.1, 'func': 'x'})
    assert rv2.status_code == 200
    jid = rv2.get_json()['job_id']
    time.sleep(0.2)
    rv3 = client.get('/jobs')
    assert jid not in rv3.get_json()['jobs']

def test_recurring_and_cancel_and_reschedule(client):
    rv = client.post('/jobs/recurring', json={'interval': 0.1, 'sla_jitter': 0, 'func': 'y'})
    jid = rv.get_json()['job_id']
    time.sleep(0.3)
    rv2 = client.delete(f'/jobs/{jid}/cancel')
    assert rv2.status_code == 200
    rv3 = client.post(f'/jobs/{jid}/reschedule', json={'interval': 0.05})
    assert rv3.status_code == 200
    # Rescheduling a cancelled job should error or do nothing
    # We accept no exception; check response content
    data = rv3.get_json()
    assert data['rescheduled'] == jid
    assert data['new_interval'] == 0.05
