import os
import time
import shutil
import threading
import logging
import pytest
from fs_watcher import Watcher

@pytest.fixture(autouse=True)
def cap_log_level():
    logging.getLogger('fs_watcher').setLevel(logging.CRITICAL)
    yield

def test_run_single_scan_detects_create_modify_delete(tmp_path):
    watch_dir = tmp_path / "data"
    watch_dir.mkdir()
    w = Watcher(str(watch_dir))
    events = []
    w.on_event(lambda e: events.append(e))
    # Initial empty scan
    w.run_single_scan()
    assert events == []
    # Create file
    f1 = watch_dir / "file1.txt"
    f1.write_text("hello")
    w.run_single_scan()
    assert events and events[-1]['type'] == 'created' and f1.as_posix() in events[-1]['path']
    # Modify file
    f1.write_text("world")
    w.run_single_scan()
    assert events and events[-1]['type'] == 'modified'
    # Delete file
    f1.unlink()
    w.run_single_scan()
    assert events and events[-1]['type'] == 'deleted'

def test_include_exclude_filters(tmp_path):
    watch_dir = tmp_path / "data"
    watch_dir.mkdir()
    w = Watcher(str(watch_dir))
    events = []
    w.set_filters(include_patterns=["*.csv"], exclude_patterns=["ignore*"])
    w.on_event(lambda e: events.append(e))
    f_csv = watch_dir / "data.csv"
    f_txt = watch_dir / "data.txt"
    f_ign = watch_dir / "ignore.csv"
    f_csv.write_text("1")
    f_txt.write_text("2")
    f_ign.write_text("3")
    w.run_single_scan()
    types = [e['type'] for e in events]
    paths = [os.path.basename(e['path']) for e in events]
    assert 'data.csv' in paths
    assert 'data.txt' not in paths
    assert 'ignore.csv' not in paths

def test_batch_dispatch(tmp_path):
    watch_dir = tmp_path / "data"
    watch_dir.mkdir()
    w = Watcher(str(watch_dir), polling_interval=0.1)
    batch_list = []
    w.on_event(lambda batch: batch_list.append(batch))
    w.batch_dispatch(interval_ms=100)
    w.start()
    # create multiple files
    for i in range(3):
        f = watch_dir / f"f{i}.txt"
        f.write_text(str(i))
    time.sleep(0.3)
    w.stop()
    # Expect at least one batch with 3 events
    assert any(len(batch) == 3 for batch in batch_list)

def test_rate_limit_global(tmp_path):
    watch_dir = tmp_path / "data"
    watch_dir.mkdir()
    w = Watcher(str(watch_dir), polling_interval=0.01)
    events = []
    w.set_throttle(rate_limit_per_sec=5)
    w.on_event(lambda e: events.append(e))
    w.start()
    for i in range(10):
        f = watch_dir / f"{i}.txt"
        f.write_text("x")
    time.sleep(0.5)
    w.stop()
    # Should not exceed ~5 events
    assert len(events) <= 6

def test_handler_rate_limit(tmp_path):
    watch_dir = tmp_path / "data"
    watch_dir.mkdir()
    w = Watcher(str(watch_dir), polling_interval=0.01)
    events = []
    def cb(e): events.append(e)
    name = w.on_event(cb)
    w.apply_rate_limit(name, max_events_per_sec=3)
    w.start()
    for i in range(5):
        f = watch_dir / f"{i}.txt"
        f.write_text("x")
    time.sleep(0.5)
    w.stop()
    assert len(events) <= 4

def test_context_manager(tmp_path):
    watch_dir = tmp_path / "data"
    watch_dir.mkdir()
    events = []
    with Watcher(str(watch_dir), polling_interval=0.01) as w:
        w.on_event(lambda e: events.append(e))
        f = watch_dir / "file.txt"
        f.write_text("hi")
        time.sleep(0.1)
    # After exit no exceptions and at least one event recorded
    assert events and events[0]['type'] == 'created'

def test_custom_polling_strategy(tmp_path):
    watch_dir = tmp_path / "data"
    watch_dir.mkdir()
    # custom strategy returns empty always
    def custom(path):
        return {}
    w = Watcher(str(watch_dir), polling_interval=0.01)
    events = []
    w.set_polling_strategy(custom)
    w.on_event(lambda e: events.append(e))
    w.start()
    f = watch_dir / "file.txt"
    f.write_text("x")
    time.sleep(0.1)
    w.stop()
    # With custom empty strategy, no events
    assert events == []
