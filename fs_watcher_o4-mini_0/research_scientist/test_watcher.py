import os
import time
import tempfile
import shutil
import threading
import pytest
import logging
from fs_watcher import Watcher

def test_configure_thread_pool():
    w = Watcher().configure_thread_pool(5)
    assert hasattr(w, '_executor')
    assert w._executor._max_workers == 5

def test_set_filters_and_run_scan(tmp_path):
    # create directory structure
    base = tmp_path / "data"
    base.mkdir()
    (base / "good.csv").write_text("1,2,3")
    (base / "calibration_bad.csv").write_text("x")
    (base / "temp.tmp").write_text("y")
    sub = base / "sub"
    sub.mkdir()
    (sub / "good2.csv").write_text("a")
    w = Watcher()
    w.set_filters(include=['data/**/*.csv'], exclude=['data/**/calibration_*', '*.tmp'])
    # monkey patch scanner to scan tmp_path
    def scanner(path):
        return [
            str(base / "good.csv"),
            str(base / "calibration_bad.csv"),
            str(base / "temp.tmp"),
            str(sub / "good2.csv"),
        ]
    w.set_polling_strategy(scanner)
    evts = w.run_single_scan(str(tmp_path))
    paths = sorted([e['src_path'] for e in evts])
    assert str(base / "good.csv") in paths
    assert str(sub / "good2.csv") in paths
    assert not any("calibration_bad" in p for p in paths)
    assert not any(p.endswith('.tmp') for p in paths)

def test_on_event_and_batch_dispatch(tmp_path):
    base = tmp_path / "data"
    base.mkdir()
    for i in range(3):
        (base / f"file{i}.csv").write_text("x")
    events = []
    batches = []
    def on_evt(e):
        events.append(e)
    def on_batch(batch):
        batches.append(batch)
    w = Watcher()
    w.set_filters(include=['data/**/*.csv'])
    w.on_event(on_evt)
    w.batch_dispatch(100)
    evts = w.run_single_scan(str(tmp_path))
    # wait for threads if any
    time.sleep(0.1)
    assert len(events) == len(evts) == 3
    assert len(batches) == 1
    assert len(batches[0]) == 3

def test_configure_logging():
    w = Watcher().configure_logging('DEBUG')
    assert w._logger.level == logging.DEBUG
    with pytest.raises(ValueError):
        Watcher().configure_logging('INVALID')

def test_apply_rate_limit_and_throttle():
    w = Watcher().apply_rate_limit('worker1', 10).set_throttle(1, 1000)
    assert w._rate_limits['worker1'] == 10
    assert w._max_events == 1
    assert w._per_ms == 1000
    # create two events to test throttle
    e1 = {'type': 'created', 'src_path': 'a', 'time': time.time()}
    # monkey patch event generation
    calls = []
    def cb(e):
        calls.append(e)
    w.on_event(cb)
    # first scan yields one event
    def scan1(path): return ['a', 'b']
    w.set_polling_strategy(scan1)
    evts1 = w.run_single_scan('')
    evts2 = w.run_single_scan('')
    # only first batch delivers events due to throttle=1 per 1s
    assert len(calls) == 1

def test_set_polling_strategy():
    base = tempfile.mkdtemp()
    def custom(path):
        return [os.path.join(path, "x.txt")]
    w = Watcher().set_polling_strategy(custom)
    ev = w.run_single_scan(base)
    assert ev[0]['src_path'].endswith("x.txt")
    shutil.rmtree(base)

def test_context_manager_shutdown():
    w = Watcher().configure_thread_pool(2)
    with w as ww:
        assert ww is w
    assert w._shutdown is True
