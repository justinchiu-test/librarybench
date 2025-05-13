import pytest
import time
from event_history_store import EventHistoryStore

def test_log_and_query():
    store = EventHistoryStore()
    t0 = time.time()
    store.log_event("file1.csv", "created", timestamp=t0)
    store.log_event("file2.csv", "modified")
    all_events = store.query()
    assert any(e[0] == "file1.csv" and e[1] == "created" for e in all_events)
    assert any(e[0] == "file2.csv" and e[1] == "modified" for e in all_events)

def test_query_filters():
    store = EventHistoryStore()
    store.log_event("a.txt", "created")
    store.log_event("a.txt", "modified")
    store.log_event("b.txt", "created")
    res1 = store.query(path="a.txt")
    assert all(r[0] == "a.txt" for r in res1)
    res2 = store.query(event_type="created")
    assert all(r[1] == "created" for r in res2)
