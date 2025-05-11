import os
import threading
import time
import tempfile
import pytest
from db.embedded_db import EmbeddedDB
from datetime import timedelta, datetime

def test_basic_set_get():
    db = EmbeddedDB()
    db.update_document('players', 'p1', {'name': 'Alice', 'level': 5})
    doc = db.get_document('players', 'p1')
    assert doc == {'name': 'Alice', 'level': 5}

def test_track_versions():
    db = EmbeddedDB()
    db.track_versions(True)
    db.update_document('inv', 'i1', {'gold': 10})
    db.update_document('inv', 'i1', {'gold': 20})
    versions = db._versions['inv']['i1']
    assert len(versions) == 2
    assert versions[0][1] == {'gold': 10}
    assert versions[1][1] == {'gold': 20}

def test_ttl_expiry():
    db = EmbeddedDB()
    db.set_ttl(0)  # expire immediately
    db.update_document('demo', 'd1', {'temp': True})
    time.sleep(0.01)
    assert db.get_document('demo', 'd1') is None

def test_stream_changes():
    db = EmbeddedDB()
    events = []
    db.stream_changes(lambda e: events.append(e))
    db.update_document('leaders', 'u1', {'score': 100})
    db.delete_document('leaders', 'u1')
    assert events[0]['type'] == 'update'
    assert events[1]['type'] == 'delete'

def test_update_merge():
    db = EmbeddedDB()
    db.update_document('profiles', 'u2', {'stats': {'hp': 100, 'mp': 50}})
    db.update_document('profiles', 'u2', {'stats': {'mp': 30}, 'name': 'Bob'}, merge=True)
    doc = db.get_document('profiles', 'u2')
    assert doc == {'stats': {'hp': 100, 'mp': 30}, 'name': 'Bob'}

def test_backup_restore():
    db = EmbeddedDB()
    db.update_document('c', 'x', {'v': 1})
    db.backup('b1')
    db.update_document('c', 'x', {'v': 2})
    db.restore('b1')
    doc = db.get_document('c', 'x')
    assert doc == {'v': 1}

def test_concurrency():
    db = EmbeddedDB()
    def writer(i):
        db.update_document('con', str(i), {'val': i})
    threads = [threading.Thread(target=writer, args=(i,)) for i in range(10)]
    for t in threads: t.start()
    for t in threads: t.join()
    ids = set(db._backend.list_ids('con'))
    assert ids == set(str(i) for i in range(10))

def test_encrypt_at_rest():
    db = EmbeddedDB()
    key = os.urandom(32)
    db.encrypt_at_rest(key)
    db.update_document('sec', 's1', {'secret': 'data'})
    # internal storage should not be plaintext
    raw = db._backend.get('sec', 's1')
    assert isinstance(raw, dict) and 'iv' in raw and 'ct' in raw
    doc = db.get_document('sec', 's1')
    assert doc == {'secret': 'data'}

def test_batch_upsert():
    db = EmbeddedDB()
    docs = [{'id': 'a', 'x': 1}, {'id': 'b', 'y': 2}]
    db.batch_upsert('items', docs)
    assert db.get_document('items', 'a') == {'x': 1}
    assert db.get_document('items', 'b') == {'y': 2}

def test_plugins():
    class P:
        def __init__(self):
            self.events = []
        def pre_save(self, col, id, data):
            self.events.append(('pre', col, id, data.copy()))
        def post_save(self, col, id, data):
            self.events.append(('post', col, id, data.copy()))
    p = P()
    db = EmbeddedDB()
    db.register_plugin(p)
    db.update_document('pl', 'z', {'num': 9})
    assert p.events[0][0] == 'pre'
    assert p.events[1][0] == 'post'

def test_filesystem_backend(tmp_path):
    base = tmp_path / "d"
    db = EmbeddedDB()
    db.set_storage_backend('filesystem', base_path=str(base))
    db.update_document('fs', 'f1', {'a': 1})
    doc = db.get_document('fs', 'f1')
    assert doc == {'a': 1}
    # file exists
    p = base / 'fs' / 'f1.json'
    assert p.exists()
