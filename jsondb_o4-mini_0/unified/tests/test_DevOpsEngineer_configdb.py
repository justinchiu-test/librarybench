import pytest
import time
import os
import tempfile
from DevOpsEngineer.configdb import ConfigDB, InMemoryBackend, ConcurrencyError, ValidationError

class DummyPlugin:
    def __init__(self):
        self.before = []
        self.after = []
    def before_update(self, key, old, new):
        self.before.append((key, old.copy(), new.copy()))
        if new.get('invalid'):
            raise ValidationError("Invalid field")
    def after_update(self, key, new):
        self.after.append((key, new.copy()))

def test_create_and_get():
    db = ConfigDB()
    db.createDocument('a', {'x':1})
    result = db.getDocument('a')
    assert result == {'x':1}
    doc, versions = db.getDocument('a', with_versions=True)
    assert doc == {'x':1}
    assert versions[0]['version'] == 1
    db.close()

def test_update_merge_and_replace():
    db = ConfigDB()
    db.createDocument('a', {'x':1, 'y':2})
    # merge update
    db.updateDocument('a', {'y':3})
    doc = db.getDocument('a')
    assert doc == {'x':1, 'y':3}
    # replace update
    db.updateDocument('a', {'z':5}, merge=False)
    doc = db.getDocument('a')
    assert doc == {'z':5}
    versions = db.getDocument('a', with_versions=True)[1]
    assert [v['version'] for v in versions] == [1,2,3]
    db.close()

def test_version_rollback():
    db = ConfigDB()
    db.createDocument('a', {'x':1})
    db.updateDocument('a', {'x':2})
    db.updateDocument('a', {'x':3})
    db.rollback('a', 2)
    doc = db.getDocument('a')
    assert doc == {'x':2}
    versions = db.getDocument('a', with_versions=True)[1]
    assert [v['version'] for v in versions] == [1,2]
    db.close()

def test_ttl_expiry():
    db = ConfigDB(sweep_interval=0.1)
    db.createDocument('a', {'x':1}, ttl=0.2)
    assert db.getDocument('a') == {'x':1}
    time.sleep(0.3)
    assert db.getDocument('a') is None
    db.close()

def test_stream_changes():
    db = ConfigDB()
    events = []
    db.streamChanges(lambda e: events.append(e))
    db.createDocument('a', {'x':1})
    db.updateDocument('a', {'x':2})
    db.deleteDocument('a')
    actions = [e['action'] for e in events]
    assert actions == ['create','update','delete']
    db.close()

def test_batch_upsert_success_and_rollback():
    db = ConfigDB()
    db.createDocument('a', {'v':1})
    items = [('a', {'v':2}), ('b', {'v':3})]
    assert db.batchUpsert(items)
    assert db.getDocument('a')['v'] == 2
    assert db.getDocument('b')['v'] == 3
    # introduce failure
    class BadPlugin:
        def before_update(self, key, old, new):
            if key == 'c':
                raise Exception("fail")
    db = ConfigDB()
    db.registerPlugin(BadPlugin())
    db.createDocument('c', {'v':1})
    with pytest.raises(Exception):
        db.batchUpsert([('c', {'v':2}), ('d', {'v':4})])
    # ensure rollback: c should still be version 1, d does not exist
    assert db.getDocument('c')['v'] == 1
    assert db.getDocument('d') is None

def test_plugin_validation():
    db = ConfigDB()
    plugin = DummyPlugin()
    db.registerPlugin(plugin)
    db.createDocument('a', {'x':1})
    # valid update
    db.updateDocument('a', {'y':2})
    assert plugin.before
    assert plugin.after
    # invalid update
    with pytest.raises(ValidationError):
        db.updateDocument('a', {'invalid':True})
    # ensure doc unchanged
    assert db.getDocument('a') == {'x':1,'y':2}

def test_concurrency_optimistic():
    db = ConfigDB()
    db.createDocument('a', {'x':1})
    # wrong expected version
    with pytest.raises(ConcurrencyError):
        db.updateDocument('a', {'x':2}, expected_version=0)
    # correct
    db.updateDocument('a', {'x':2}, expected_version=1)
    assert db.getDocument('a')['x'] == 2

def test_concurrency_pessimistic():
    db = ConfigDB()
    db.createDocument('a', {'x':1})
    lock = db.locks['a']
    lock.acquire()
    with pytest.raises(ConcurrencyError):
        db.updateDocument('a', {'x':2}, lock_type='pessimistic')
    lock.release()
    # now works
    db.updateDocument('a', {'x':3}, lock_type='pessimistic')
    assert db.getDocument('a')['x'] == 3

def test_backup_and_restore(tmp_path):
    db = ConfigDB()
    db.createDocument('a', {'x':1})
    db.updateDocument('a', {'x':2})
    backup_file = tmp_path / "backup.pkl"
    db.backup(str(backup_file))
    # clear and restore
    db2 = ConfigDB()
    db2.restore(str(backup_file))
    assert db2.getDocument('a') == {'x':2}
    versions = db2.getDocument('a', with_versions=True)[1]
    assert [v['version'] for v in versions] == [1,2]
    db.close()
    db2.close()

def test_switch_backend():
    db = ConfigDB()
    db.createDocument('a', {'x':1})
    backend = InMemoryBackend()
    db.setStorageBackend(backend)
    # old data: backend is new so no data
    assert db.getDocument('a') is None
    db.createDocument('b', {'y':2})
    # fixed stray quote here
    assert db.getDocument('b') == {'y':2}
    db.close()
