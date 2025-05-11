import pytest
from alice_data_analyst.service import create_app

@pytest.fixture
def client(tmp_path):
    key = b'\x00' * 32
    app = create_app(str(tmp_path), key)
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

def test_health(client):
    rv = client.get('/health')
    assert rv.status_code == 200
    assert rv.get_json()['status'] == 'ok'

def test_insert_get_event(client):
    rv = client.post('/events', json={'campaign': 'camp1'})
    assert rv.status_code == 201
    ev = rv.get_json()
    id_ = ev['id']
    rv2 = client.get(f'/events/{id_}')
    assert rv2.status_code == 200
    got = rv2.get_json()
    assert got['campaign'] == 'camp1'
    assert got['normalized'] is True

def test_update_event(client):
    rv = client.post('/events', json={'campaign': 'c'})
    id_ = rv.get_json()['id']
    rv2 = client.put(f'/events/{id_}', json={'new_field': 42})
    assert rv2.status_code == 200
    got = rv2.get_json()
    assert got['new_field'] == 42

def test_soft_delete_and_undelete(client):
    rv = client.post('/events', json={'campaign': 'c'})
    id_ = rv.get_json()['id']
    rv2 = client.delete(f'/events/{id_}')
    assert rv2.status_code == 204
    rv3 = client.post(f'/events/{id_}/undelete')
    assert rv3.status_code == 204
    rv4 = client.get(f'/events/{id_}')
    assert rv4.status_code == 200
    assert rv4.get_json()['deleted'] is False

def test_purge_event(client):
    rv = client.post('/events', json={'campaign': 'c'})
    id_ = rv.get_json()['id']
    rv2 = client.delete(f'/events/{id_}?soft=false')
    assert rv2.status_code == 204
    rv3 = client.get(f'/events/{id_}')
    assert rv3.status_code == 404

def test_versions_and_restore(client):
    rv = client.post('/events', json={'campaign': 'c', 'val': 1})
    id_ = rv.get_json()['id']
    client.put(f'/events/{id_}', json={'val': 2})
    client.put(f'/events/{id_}', json={'val': 3})
    rvv = client.get(f'/events/{id_}/versions')
    vers = rvv.get_json()['versions']
    assert vers == [1, 2, 3]
    rvr = client.post(f'/events/{id_}/versions/1')
    got = rvr.get_json()
    assert got['val'] == 1

def test_query_filters(client):
    from datetime import datetime, timedelta
    now = datetime.utcnow()
    e1 = client.post('/events', json={'campaign': 'A', 'timestamp': now.isoformat()}).get_json()
    client.post('/events', json={'campaign': 'B', 'timestamp': (now - timedelta(days=1)).isoformat()})
    client.post('/events', json={'campaign': 'A', 'timestamp': (now + timedelta(days=1)).isoformat()})
    rv = client.get('/events?campaign=A')
    res = rv.get_json()
    assert len(res) == 2
    start = (now - timedelta(hours=1)).isoformat()
    end = (now + timedelta(hours=1)).isoformat()
    rv2 = client.get(f'/events?start={start}&end={end}')
    res2 = rv2.get_json()
    assert len(res2) == 1 and res2[0]['id'] == e1['id']

def test_batch_upsert(client):
    evs = [{'campaign': 'x'}, {'campaign': 'y'}]
    rv = client.post('/events/batch', json=evs)
    assert rv.status_code == 201
    res = rv.get_json()
    assert len(res) == 2
    for e in res:
        r = client.get(f"/events/{e['id']}")
        assert r.status_code == 200

def test_metrics(client):
    client.get('/health')
    client.get('/health')
    rv = client.get('/metrics')
    data = rv.get_data(as_text=True)
    assert 'request_count' in data
