import os
import tempfile
import threading
import time
import pytest
from ComplianceOfficer.compliance_repo.store import ComplianceStore

def test_basic_upsert_andVersioning():
    cs = ComplianceStore()
    cs.updateDocument('a', {'x':1})
    cs.updateDocument('a', {'y':2})
    doc = cs.getDocument('a')
    assert doc == {'x':1,'y':2}
    vers = cs.getVersions('a')
    assert len(vers) == 2
    assert vers[0] == {'x':1}
    assert vers[1] == {'x':1,'y':2}
    # rollback
    old = cs.rollbackVersion('a',0)
    assert cs.getDocument('a') == {'x':1}

def test_ttl_and_purge():
    cs = ComplianceStore()
    cs.updateDocument('t', {'data':'d'})
    cs.setTTL('t', 1)  # 1 second
    time.sleep(1.1)
    cs.purgeExpired()
    assert cs.getDocument('t') is None

def test_streaming_and_plugins():
    cs = ComplianceStore()
    events = []
    def subscriber(evt): events.append(evt)
    cs.streamChanges(subscriber)
    cs.registerPlugin(lambda e: events.append({'plugin':e}))
    cs.updateDocument('d1', {'a':1})
    assert any(e.get('type')=='update' for e in events)
    assert any('plugin' in e for e in events)

def test_merge_semantics():
    cs = ComplianceStore()
    cs.updateDocument('m', {'a':1,'b':2})
    cs.updateDocument('m', {'b':3,'c':4})
    doc = cs.getDocument('m')
    assert doc == {'a':1,'b':3,'c':4}

def test_concurrency():
    cs = ComplianceStore()
    cs.updateDocument('con', {'v':0})
    def inc():
        for _ in range(100):
            d = cs.getDocument('con')
            cs.updateDocument('con', {'v': d['v']+1})
    threads = [threading.Thread(target=inc) for _ in range(5)]
    for t in threads: t.start()
    for t in threads: t.join()
    final = cs.getDocument('con')['v']
    assert final == 5*100

def test_batch_upsert_and_event():
    cs = ComplianceStore()
    events = []
    cs.streamChanges(events.append)
    docs = [{'id':'b1','a':1},{'id':'b2','x':9}]
    cs.batchUpsert(docs)
    assert cs.getDocument('b1')['a']==1
    assert cs.getDocument('b2')['x']==9
    # check batch event
    assert any(e['type']=='batch' for e in events)

def test_backup_and_restore(tmp_path):
    cs = ComplianceStore()
    cs.updateDocument('p', {'k':'v'})
    cs.setTTL('p', 10)
    fp = tmp_path / "bak.dat"
    cs.backup(str(fp))
    # new store
    cs2 = ComplianceStore()
    cs2.restore(str(fp))
    assert cs2.getDocument('p') == {'k':'v'}
    assert len(cs2.getVersions('p')) == 1

def test_encrypt_at_rest():
    cs = ComplianceStore()
    key = b'key123'
    cs.encryptAtRest(key)
    cs.updateDocument('e', {'s':'secret'})
    # internal storage is encrypted
    raw = cs._store['e']
    assert raw != json.dumps({'s':'secret'}).encode()
    # retrieval is correct
    got = cs.getDocument('e')
    assert got == {'s':'secret'}

def test_storage_backend_file(tmp_path):
    d = tmp_path / "db"
    cs = ComplianceStore()
    cs.setStorageBackend('file', directory=str(d))
    cs.updateDocument('f1', {'n':5})
    # file exists
    path = d / "f1.json"
    assert path.exists()
    # read raw file
    data = path.read_bytes()
    assert b'"n": 5' in data
    # get back
    got = cs.getDocument('f1')
    assert got == {'n':5}

def test_restore_notifies():
    cs = ComplianceStore()
    notified = []
    cs.streamChanges(notified.append)
    # make a backup first
    cs.updateDocument('x',{'v':1})
    f = tempfile.NamedTemporaryFile(delete=False)
    f.close()
    cs.backup(f.name)
    cs.restore(f.name)
    assert any(e['type']=='restore' for e in notified)
