import pytest
import time
from IoTManager.edge_db import EdgeJSONDB, DocumentNotFoundError, VersionConflictError, BatchUpsertError

def test_insert_and_get():
    db = EdgeJSONDB()
    db.insert_document('sensor1', {'temp': 22})
    doc = db.get_document('sensor1')
    assert doc == {'temp': 22}

def test_versioning_and_history():
    db = EdgeJSONDB()
    db.insert_document('dev', {'a': 1})
    db.update_document('dev', {'b': 2})
    db.update_document('dev', {'a': 3})
    versions = db.get_versions('dev')
    assert len(versions) == 3
    assert versions[0]['document'] == {'a': 1}
    assert versions[1]['document'] == {'a': 1, 'b': 2}
    assert versions[2]['document'] == {'a': 3, 'b': 2}

def test_rollback():
    db = EdgeJSONDB()
    db.insert_document('x', {'v': 1})
    db.update_document('x', {'v': 2})
    db.update_document('x', {'v': 3})
    # rollback to version 2
    db.rollback('x', 2)
    doc = db.get_document('x')
    assert doc['v'] == 2
    versions = db.get_versions('x')
    assert versions[-1]['version'] == 4  # new version after rollback

def test_update_full_replace():
    db = EdgeJSONDB()
    db.insert_document('d', {'a': 1, 'b': 2})
    db.update_document('d', {'c': 3}, full_replace=True)
    doc = db.get_document('d')
    assert doc == {'c': 3}

def test_optimistic_locking():
    db = EdgeJSONDB()
    db.insert_document('o', {'x': 1})
    meta = db.get_metadata('o')
    with pytest.raises(VersionConflictError):
        db.update_document('o', {'x': 2}, expected_version=meta['version'] + 1)

def test_batch_upsert_success_and_failure():
    db = EdgeJSONDB()
    db.insert_document('a', {'x': 1})
    # successful batch
    db.batch_upsert({'a': {'x': 2}, 'b': {'y': 10}})
    assert db.get_document('a')['x'] == 2
    assert db.get_document('b')['y'] == 10
    # failing batch rolls back
    class FailPlugin:
        def on_insert(self, key, doc, meta):
            if key == 'c':
                raise Exception("fail")
    db = EdgeJSONDB()
    db.register_plugin('fp', FailPlugin())
    with pytest.raises(BatchUpsertError):
        db.batch_upsert({'c': {'k': 1}, 'd': {'k': 2}})
    with pytest.raises(DocumentNotFoundError):
        db.get_document('c')
    with pytest.raises(DocumentNotFoundError):
        db.get_document('d')

def test_stream_changes():
    db = EdgeJSONDB()
    events = []
    def cb(event, key, doc):
        events.append((event, key, doc))
    db.stream_changes(cb)
    db.insert_document('s', {'v': 5})
    db.update_document('s', {'v': 6})
    assert events[0][0] == 'insert'
    assert events[1][0] == 'update'
    assert events[1][2]['v'] == 6

def test_ttl_expiry():
    db = EdgeJSONDB()
    db.insert_document('t1', {'x': 1})
    db.set_ttl(1)
    # manually backdate updated_at
    md = db.get_metadata('t1')
    old = (time.time() - 10)
    # convert to isoformat
    past = datetime = None
    import datetime as _dt
    md['updated_at'] = (_dt.datetime.utcnow() - _dt.timedelta(seconds=10)).isoformat()
    db._storage.save('t1', db.get_document('t1'), md)
    db.cleanup_expired()
    with pytest.raises(DocumentNotFoundError):
        db.get_document('t1')

def test_backup_restore():
    db = EdgeJSONDB()
    db.insert_document('p', {'z': 9})
    backup = db.backup()
    db.insert_document('q', {'z': 10})
    db.restore(backup)
    # 'q' should not exist
    with pytest.raises(DocumentNotFoundError):
        db.get_document('q')
    # 'p' exists
    assert db.get_document('p')['z'] == 9

def test_register_plugin_hooks():
    db = EdgeJSONDB()
    calls = []
    class P:
        def on_insert(self, key, doc, meta):
            calls.append(('i', key))
        def on_update(self, key, doc, meta):
            calls.append(('u', key))
    db.register_plugin('p', P())
    db.insert_document('k1', {'a': 1})
    db.update_document('k1', {'a': 2})
    assert ('i', 'k1') in calls
    assert ('u', 'k1') in calls

def test_set_storage_backend_errors():
    db = EdgeJSONDB()
    with pytest.raises(ValueError):
        db.set_storage_backend('unknown')
    db = EdgeJSONDB()
    # switching to fs backend (creates folder)
    db.set_storage_backend('fs', base_path='./testdata')
    db.insert_document('fs1', {'a': 1})
    assert db.get_document('fs1')['a'] == 1
    # cleanup fs folder
    import shutil
    shutil.rmtree('./testdata', ignore_errors=True)
