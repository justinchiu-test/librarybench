import json
import os
from pathlib import Path
import pytest
from watcher.api import app, events, snapshots

@pytest.fixture(autouse=True)
def clear_events_snapshots():
    events.clear()
    snapshots.clear()
    yield
    events.clear()
    snapshots.clear()

def test_get_events_empty(client):
    res = client.get('/events')
    assert res.status_code == 200
    assert res.json == []

def test_snapshot_endpoint(tmp_path, client):
    # create file
    (tmp_path/"file.txt").write_text("data")
    res = client.post('/snapshot', json={"root": str(tmp_path)})
    assert res.status_code == 200
    body = res.json
    assert "snapshot" in body and "diff" in body
    assert body["snapshot"].get("file.txt")
    # second snapshot
    (tmp_path/"file2.txt").write_text("more")
    res2 = client.post('/snapshot', json={"root": str(tmp_path)})
    assert res2.status_code == 200
    body2 = res2.json
    assert "added" in body2["diff"]
    assert body2["diff"]["added"] == ["file2.txt"]
    # events stored
    ev = client.get('/events').json
    assert len(ev) == 2

@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as c:
        yield c
