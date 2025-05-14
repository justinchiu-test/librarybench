import os
import logging
import time
import tempfile
import shutil
import fnmatch
import pytest
from fs_watcher import Watcher

def test_configuration_methods():
    w = Watcher({'foo': 'bar'})
    assert w.config == {'foo': 'bar'}
    w.configure_thread_pool(5)
    assert w.pool_size == 5
    w.set_filters(include=['*.log'], exclude=['*.old'])
    assert w.include == ['*.log']
    assert w.exclude == ['*.old']
    w.set_throttle(100)
    assert w.events_per_sec == 100
    def cb(x): pass
    w.on_event(cb)
    assert w.callback == cb
    w.batch_dispatch(200)
    assert w.batch_interval_ms == 200
    w.configure_logging('ERROR')
    assert w.logger.level == logging.ERROR
    strategy = object()
    w.set_polling_strategy(strategy)
    assert w.polling_strategy is strategy
    w.apply_rate_limit('siem_submitter', 20)
    assert 'siem_submitter' in w.rate_limits
    assert w.rate_limits['siem_submitter']['limit'] == 20

def test_context_manager():
    w = Watcher()
    assert not w.running
    with w as ww:
        assert ww.running
    assert not w.running

def test_run_single_scan_and_filters(tmp_path):
    # Create directory structure
    dirpath = tmp_path / "logs"
    dirpath.mkdir()
    a = dirpath / "a.log"
    b = dirpath / "b.old"
    debug = dirpath / "debug"
    debug.mkdir()
    c = debug / "c.log"
    for f in [a, b, c]:
        f.write_text("content")
    w = Watcher()
    w.set_filters(include=[str(dirpath / "*.log")], exclude=[str(dirpath / "*.old"), str(debug / "*")])
    results = w.run_single_scan(str(dirpath))
    assert len(results) == 1
    assert results[0].endswith('a.log')

def test_throttle_without_batch():
    w = Watcher()
    received = []
    w.set_throttle(2)
    w.on_event(lambda evs: received.extend(evs))
    with w:
        w.simulate_event('file1.log', 'created')
        w.simulate_event('file2.log', 'modified')
        w.simulate_event('file3.log', 'deleted')
    assert len(received) == 2

def test_batch_dispatch_and_rate_limit():
    w = Watcher()
    received = []
    w.batch_dispatch(1000)
    w.apply_rate_limit('siem_submitter', 2)
    w.on_event(lambda evs: received.extend(evs))
    with w:
        # simulate 3 events
        w.simulate_event('f1.log', 'created')
        w.simulate_event('f2.log', 'modified')
        w.simulate_event('f3.log', 'deleted')
        # flush batch manually
        w.flush_batch()
    assert len(received) == 2
    paths = [e['path'] for e in received]
    assert 'f1.log' in paths and 'f2.log' in paths

def test_filtering_of_events():
    w = Watcher()
    received = []
    w.set_filters(include=['*.log'], exclude=['debug/*'])
    w.on_event(lambda evs: received.extend(evs))
    with w:
        w.simulate_event('app.log', 'modified')
        w.simulate_event('debug/foo.log', 'modified')
    assert len(received) == 1
    assert received[0]['path'] == 'app.log'

def test_polling_strategy_and_logging(monkeypatch):
    w = Watcher()
    strategy = lambda: 'inotify'
    w.set_polling_strategy(strategy)
    assert w.polling_strategy() == 'inotify'
    w.configure_logging('DEBUG')
    assert w.logger.level == logging.DEBUG

def test_flush_empty_batch_does_nothing():
    w = Watcher()
    received = []
    w.batch_dispatch(100)
    w.on_event(lambda evs: received.extend(evs))
    with w:
        w.flush_batch()
    assert received == []

def test_rate_limit_resets_after_window(monkeypatch):
    w = Watcher()
    received = []
    w.on_event(lambda evs: received.extend(evs))
    w.batch_dispatch(100)
    w.apply_rate_limit('siem_submitter', 1)
    with w:
        w.simulate_event('x.log', 'c')
        w.simulate_event('y.log', 'c')
        w.flush_batch()
        assert len(received) == 1
        # advance time beyond 1 second window
        old = w.rate_limits['siem_submitter']['window_start']
        w.rate_limits['siem_submitter']['window_start'] = old - 2
        w.simulate_event('z.log', 'c')
        w.flush_batch()
    assert len(received) == 2
