import os
import time
import tempfile
import threading
import logging
import pytest
from fs_watcher import Watcher

def test_configure_thread_pool():
    watcher = Watcher()
    watcher.configure_thread_pool(5)
    assert watcher._max_workers == 5
    assert watcher._executor._max_workers == 5

def test_set_filters():
    watcher = Watcher()
    watcher.set_filters(include=['src/*.py'], exclude=['.git/', '*.log'])
    assert watcher._include == ['src/*.py']
    assert watcher._exclude == ['.git/', '*.log']

def test_set_throttle():
    watcher = Watcher()
    watcher.set_throttle(2, 1000)
    assert watcher._throttle_limit == 2
    assert watcher._throttle_window == 1.0

def test_on_event_and_emit():
    watcher = Watcher()
    received = []
    watcher.on_event(lambda e: received.append(e))
    watcher._emit_event({'type': 'test', 'path': 'file.txt', 'timestamp': time.time()})
    # no batch, no filters, throttle allows
    time.sleep(0.1)
    assert len(received) == 1
    assert received[0]['type'] == 'test'

def test_batch_dispatch():
    watcher = Watcher()
    received = []
    watcher.on_event(lambda batch: received.append(batch))
    watcher.batch_dispatch(100)
    # emit several events
    for i in range(3):
        watcher._emit_event({'type': 'b', 'path': f'x{i}', 'timestamp': time.time()})
    time.sleep(0.2)
    # Should have one batch of size 3
    assert len(received) >= 1
    sizes = [len(b) for b in received]
    assert any(sz == 3 for sz in sizes)

def test_configure_logging():
    watcher = Watcher()
    watcher.configure_logging('DEBUG')
    assert watcher._logger.level == logging.DEBUG
    with pytest.raises(ValueError):
        watcher.configure_logging('INVALID')

def test_set_polling_strategy():
    watcher = Watcher()
    strat = object()
    watcher.set_polling_strategy(strat)
    assert watcher._polling_strategy is strat

def test_apply_rate_limit():
    watcher = Watcher()
    watcher.apply_rate_limit('uploader', 10)
    assert watcher._rate_limits['uploader'] == 10

def test_run_single_scan(tmp_path):
    # create files
    d = tmp_path / "repo"
    d.mkdir()
    f1 = d / "a.txt"
    f2 = d / "b.txt"
    f1.write_text("hello")
    f2.write_text("world")
    watcher = Watcher()
    received = []
    watcher.on_event(lambda e: received.append(e))
    watcher.run_single_scan(str(d))
    # two created events
    paths = sorted([e['path'] for e in received])
    assert os.path.join(str(d), "a.txt") in paths
    assert os.path.join(str(d), "b.txt") in paths

def test_context_manager_lifecycle():
    watcher = Watcher()
    watcher.configure_thread_pool(2)
    watcher.batch_dispatch(50)
    # register dummy
    watcher.on_event(lambda e: None)
    with watcher as w:
        assert w is watcher
        assert watcher._executor is not None
        assert watcher._running
    # after exit
    assert not watcher._running
    # executor should be shutdown; submitting should error
    with pytest.raises(Exception):
        watcher._executor.submit(lambda: None)
