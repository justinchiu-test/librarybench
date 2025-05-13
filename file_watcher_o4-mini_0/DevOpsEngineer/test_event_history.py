import pytest
from file_watcher.core import EventHistoryStore, Event

def test_history_store_basic():
    store = EventHistoryStore(max_size=3)
    e1 = Event('p1', 't1')
    e2 = Event('p2', 't2')
    store.add(e1)
    store.add(e2)
    assert store.get_events() == [e1, e2]

def test_history_rollover():
    store = EventHistoryStore(max_size=2)
    e1 = Event('p1', 't1')
    e2 = Event('p2', 't2')
    e3 = Event('p3', 't3')
    store.add(e1)
    store.add(e2)
    store.add(e3)
    events = store.get_events()
    assert events == [e2, e3]

def test_history_filtering():
    store = EventHistoryStore(max_size=5)
    e1 = Event('a.conf', 'modify')
    e2 = Event('b.txt', 'modify')
    store.add(e1)
    store.add(e2)
    res = store.get_events(lambda e: e.path.endswith('.conf'))
    assert res == [e1]
