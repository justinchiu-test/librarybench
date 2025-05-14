import os
import time
import http.client
import json
import threading
import pytest
from journaling.db import JournalDB

@pytest.fixture(scope='module')
def server(tmp_path):
    key = os.urandom(32)
    db = JournalDB(str(tmp_path), key)
    port = 8001
    server = db.startRestServer(port)
    time.sleep(0.1)
    return port

def request(method, path, body=None, port=8001):
    conn = http.client.HTTPConnection('localhost', port)
    headers = {}
    data = None
    if body is not None:
        data = json.dumps(body)
        headers['Content-Type'] = 'application/json'
    conn.request(method, path, body=data, headers=headers)
    resp = conn.getresponse()
    body = resp.read()
    try:
        return resp.status, json.loads(body.decode())
    except:
        return resp.status, body

def test_rest_crud(server):
    port = server
    # create
    entry = {
        'id': 'r1',
        'content': 'rest',
        'tags': [],
        'attachments': [],
        'metadata': {},
        'created_at': time.time(),
        'updated_at': time.time()
    }
    status, data = request('POST', '/entries', entry, port)
    assert status == 200
    # list
    status, data = request('GET', '/entries', None, port)
    assert status == 200
    assert any(e['id']=='r1' for e in data)
    # get by id
    status, data = request('GET', '/entries/r1', None, port)
    assert status == 200 and data['id']=='r1'
    # delete
    status, data = request('DELETE', '/entries/r1', None, port)
    assert status == 200
    status, data = request('GET', '/entries/r1', None, port)
    assert status == 404
