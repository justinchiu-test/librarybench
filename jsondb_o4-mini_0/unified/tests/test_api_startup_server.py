import os
import threading
import time
import requests
import tempfile
import shutil
import pytest
from api_startup.server import start_rest_server

@pytest.fixture(scope="module")
def server_instance():
    dirpath = tempfile.mkdtemp()
    host = '127.0.0.1'
    port = 5001
    path = os.path.join(dirpath, 'events.json')
    t = threading.Thread(target=start_rest_server, args=(host, port, path, b'key123456789012'), daemon=True)
    t.start()
    # wait server
    time.sleep(1)
    yield f'http://{host}:{port}', dirpath
    shutil.rmtree(dirpath)

def test_rest_upsert_and_get(server_instance):
    base, _ = server_instance
    url = base + '/events'
    evt = {'timestamp': time.time(), 'userID': 'rest', 'eventType': 'r'}
    r = requests.post(url, json=evt)
    assert r.status_code == 201
    eid = r.json()['id']
    r2 = requests.get(f'{base}/events/{eid}')
    assert r2.status_code == 200
    data = r2.json()
    assert data['id'] == eid and data['userID'] == 'rest'

def test_rest_batch_and_list(server_instance):
    base, _ = server_instance
    url = base + '/events/batch'
    evts = [
        {'timestamp': time.time(), 'userID': 'b1', 'eventType': 'e1'},
        {'timestamp': time.time(), 'userID': 'b2', 'eventType': 'e2'}
    ]
    r = requests.post(url, json=evts)
    assert r.status_code == 201
    ids = r.json()['ids']
    r2 = requests.get(base + '/events')
    assert r2.status_code == 200
    data = r2.json()
    ids_listed = [e['id'] for e in data]
    for i in ids:
        assert i in ids_listed

def test_rest_delete_and_undelete(server_instance):
    base, _ = server_instance
    evt = {'timestamp': time.time(), 'userID': 'del', 'eventType': 'd'}
    r = requests.post(base + '/events', json=evt)
    eid = r.json()['id']
    # soft delete
    r2 = requests.delete(f'{base}/events/{eid}?soft=true')
    assert r2.status_code == 204
    r3 = requests.get(base + '/events')
    assert all(e['id'] != eid for e in r3.json())
    # undelete
    r4 = requests.post(f'{base}/events/{eid}/undelete')
    assert r4.status_code == 204
    r5 = requests.get(base + '/events')
    assert any(e['id'] == eid for e in r5.json())
    # hard delete
    r6 = requests.delete(f'{base}/events/{eid}')
    assert r6.status_code == 204
    r7 = requests.get(base + '/events')
    assert all(e['id'] != eid for e in r7.json())
