import pytest
from watcher.api import app
import json

@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as c:
        yield c

def test_api_flow(client):
    # start watcher
    rv = client.post('/start', json={"batch_size": 5})
    data = rv.get_json()
    wid = data["watcher_id"]
    # inject events
    rv = client.post('/inject', json={"watcher_id": wid, "event": {"type":"create","file":"a.txt"}})
    assert rv.status_code == 200
    # get results
    rv = client.get('/results', query_string={"watcher_id": wid})
    data = rv.get_json()
    assert data["events"] == [{"type":"create","file":"a.txt"}]
    # stop watcher
    rv = client.post('/stop', json={"watcher_id": wid})
    assert rv.status_code == 200
    rv = client.get('/results', query_string={"watcher_id": wid})
    assert rv.status_code == 404
