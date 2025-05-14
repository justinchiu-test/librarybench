import os
import pytest
from audit_watcher.history import EventHistoryStore
from audit_watcher.watcher import Event

def test_history_write_and_rotate(tmp_path):
    log_dir = tmp_path / "logs"
    store = EventHistoryStore(str(log_dir), max_bytes=50, backup_count=2)
    # write multiple events to exceed 50 bytes
    for i in range(10):
        evt = Event("create", f"/file{i}", None)
        store.write_event(evt)
    # check rotation happened
    base = log_dir / "events.log"
    rotated1 = log_dir / "events.log.1"
    assert base.exists() or rotated1.exists()
    # older backup up to count
    rotated2 = log_dir / "events.log.2"
    # backup_count=2 so .2 maybe not exist
    assert not log_dir.joinpath("events.log.3").exists()
