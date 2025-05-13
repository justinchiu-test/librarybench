import json
import pytest
from iot.web_dashboard import app, update_status, record_metrics

@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as c:
        yield c

def test_status_empty(client):
    rv = client.get('/status')
    data = json.loads(rv.data)
    assert 'metrics' in data
    assert 'status' in data

def test_update_and_metrics(client):
    update_status(groups={'g1':'ok'}, progress={'g1':50}, errors={'g2':'err'})
    record_metrics(success=True, failure=True, retry_id="r1", latency=0.2)
    rv = client.get('/status')
    data = json.loads(rv.data)
    assert data['status']['groups']['g1'] == 'ok'
    assert data['status']['progress']['g1'] == 50
    assert data['status']['errors']['g2'] == 'err'
    assert data['metrics']['success_count'] == 1
    assert data['metrics']['failure_count'] == 1
    assert data['metrics']['retry_counts']['r1'] == 1
    assert abs(data['metrics']['avg_latency'] - 0.2) < 1e-6
