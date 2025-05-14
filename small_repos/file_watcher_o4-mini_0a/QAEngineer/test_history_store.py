import time
import pytest
from watcher.history_store import HistoryStore

def test_add_and_query():
    hs = HistoryStore()
    hs.add('file1', 'create')
    time.sleep(0.001)
    hs.add('file2', 'modify')
    all_events = hs.query()
    assert len(all_events) == 2
    assert len(hs.query(path='file1')) == 1
    mod = hs.query(event_type='modify')
    assert len(mod) == 1
    assert mod[0]['path'] == 'file2'
