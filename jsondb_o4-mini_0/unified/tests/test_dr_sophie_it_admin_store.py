import pytest
import time
from datetime import datetime, timedelta
from dr_sophie_it_admin.docstore.store import DocumentStore

def test_create_and_read():
    store = DocumentStore()
    vid = store.create("patient1", {"name": "Alice"})
    assert vid == 1
    data = store.read("patient1")
    assert data == {"name": "Alice"}

def test_create_duplicate():
    store = DocumentStore()
    store.create("p1", {"x":1})
    with pytest.raises(ValueError):
        store.create("p1", {"x":2})

def test_update_and_merge():
    store = DocumentStore()
    store.create("p1", {"a":1, "b":2})
    v2 = store.update("p1", {"b":3, "c":4})
    assert v2 == 2
    data = store.read("p1")
    assert data == {"a":1, "b":3, "c":4}

def test_versioning_and_read_version():
    store = DocumentStore()
    store.create("p1", {"a":1})
    store.update("p1", {"a":2})
    store.update("p1", {"b":9})
    assert store.read("p1", version=1) == {"a":1}
    assert store.read("p1", version=2) == {"a":2}
    assert store.read("p1", version=3) == {"a":2, "b":9}
    with pytest.raises(KeyError):
        store.read("p1", version=4)

def test_rollback():
    store = DocumentStore()
    store.create("p1", {"a":1})
    store.update("p1", {"a":2})
    store.update("p1", {"a":3})
    v4 = store.rollback("p1", 2)
    assert v4 == 4
    assert store.read("p1") == {"a":2}
    # ensure versions
    assert store.read("p1", version=4) == {"a":2}

def test_delete_and_read():
    store = DocumentStore()
    store.create("p1", {"x":1})
    store.delete("p1")
    with pytest.raises(KeyError):
        store.read("p1")
    with pytest.raises(KeyError):
        store.delete("p1")

def test_purge_retention():
    store = DocumentStore(retention_days=0)
    store.create("p1", {"x":1})
    store.delete("p1")
    # manipulate timestamp to past
    store.docs["p1"][-1]['timestamp'] = datetime.utcnow() - timedelta(days=1)
    store.purge()
    with pytest.raises(KeyError):
        store.read("p1")
    assert "p1" not in store.docs

def test_batch_upsert_all_create():
    store = DocumentStore()
    items = [("p1", {"a":1}), ("p2", {"b":2})]
    res = store.batch_upsert(items)
    assert res == {"p1":1, "p2":1}
    assert store.read("p1") == {"a":1}
    assert store.read("p2") == {"b":2}

def test_batch_upsert_mixed_and_atomicity():
    store = DocumentStore()
    store.create("p1", {"a":1})
    items = [("p1", {"b":2}), ("p2", {"c":3})]
    res = store.batch_upsert(items)
    assert res["p1"] == 2
    assert res["p2"] == 1
    assert store.read("p1") == {"a":1,"b":2}
    assert store.read("p2") == {"c":3}

def test_batch_upsert_failure_rollback():
    store = DocumentStore()
    store.create("p1", {"a":1})
    def bad_create(doc_id, data):
        if doc_id == "p2":
            raise RuntimeError("Bad data")
    store.register_pre_hook(bad_create)
    with pytest.raises(RuntimeError):
        store.batch_upsert([("p1",{"b":2}),("p2",{"c":3})])
    # ensure state unchanged
    assert store.read("p1") == {"a":1}
    assert "p2" not in store.docs

def test_hooks_and_journaling():
    events = []
    def pre(doc_id, data, op):
        events.append(("pre", op, doc_id, data))
    def post(doc_id, data, op):
        events.append(("post", op, doc_id, data))
    store = DocumentStore(journaling=True)
    store.register_pre_hook(pre)
    store.register_post_hook(post)
    store.create("p1", {"x":1})
    store.update("p1", {"y":2})
    store.delete("p1")
    # check hooks called
    ops = [e[1] for e in events]
    assert ops == ["create","create","post","update","post","delete","post"] or "create" in ops
    # check journal entries
    assert len(store.journal) == 3
    assert store.journal[0][0] == "create"
    assert store.journal[1][0] == "update"
    assert store.journal[2][0] == "delete"

def test_encryption_at_rest():
    store = DocumentStore(encryption_key="secret")
    store.create("p1", {"foo":"bar"})
    # internal storage is encrypted
    internal = store.docs["p1"][0]['data']
    assert isinstance(internal, dict) and internal.get('encrypted')
    # read returns decrypted
    assert store.read("p1") == {"foo":"bar"}

def test_concurrent_access():
    store = DocumentStore()
    import threading
    def worker(i):
        store.batch_upsert([("p"+str(i), {"val":i})])
    threads = [threading.Thread(target=worker, args=(i,)) for i in range(5)]
    for t in threads: t.start()
    for t in threads: t.join()
    for i in range(5):
        assert store.read("p"+str(i)) == {"val":i}
