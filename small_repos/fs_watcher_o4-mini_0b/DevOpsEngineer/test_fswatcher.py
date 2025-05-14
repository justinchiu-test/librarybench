import os
import time
import asyncio
import pytest
from fswatcher import (
    watch_directory, register_callback, unregister_callback, set_polling_strategy,
    configure_logging, configure_rate_limit, generate_change_summary,
    get_async_watcher, single_scan, set_retry_policy, stop_watcher, FileEvent
)

@pytest.fixture(autouse=True)
def cleanup():
    # ensure watcher is stopped before and after tests
    stop_watcher()
    yield
    stop_watcher()

def test_single_scan(tmp_path):
    d = tmp_path / "scan_test"
    d.mkdir()
    f1 = d / "a.txt"
    f1.write_text("hello")
    sub = d / "subdir"
    sub.mkdir()
    f2 = sub / "b.txt"
    f2.write_text("world")
    files = single_scan(str(d))
    assert str(f1) in files
    assert str(f2) in files

def test_watch_create_modify_delete(tmp_path):
    set_polling_strategy(lambda: 0.1)
    events = []
    def handler(ev):
        events.append(ev)
    register_callback("*.txt", handler)
    watch_directory(str(tmp_path))
    # create
    f = tmp_path / "x.txt"
    f.write_text("1")
    time.sleep(0.3)
    assert any(ev.event_type == 'created' and ev.src_path.endswith("x.txt") for ev in events)
    # modify
    f.write_text("2")
    time.sleep(0.3)
    assert any(ev.event_type == 'modified' and ev.src_path.endswith("x.txt") for ev in events)
    # delete
    f.unlink()
    time.sleep(0.3)
    assert any(ev.event_type == 'deleted' and ev.src_path.endswith("x.txt") for ev in events)

def test_move_event(tmp_path):
    set_polling_strategy(lambda: 0.1)
    events = []
    def handler(ev):
        events.append(ev)
    register_callback("*.txt", handler)
    watch_directory(str(tmp_path))
    f = tmp_path / "a.txt"
    f.write_text("a")
    time.sleep(0.3)
    new = tmp_path / "b.txt"
    f.rename(new)
    time.sleep(0.3)
    assert any(ev.event_type == 'moved' and ev.src_path.endswith("a.txt") and ev.dest_path.endswith("b.txt") for ev in events)

def test_unregister_callback(tmp_path):
    set_polling_strategy(lambda: 0.1)
    events = []
    def handler(ev):
        events.append(ev)
    cid = register_callback("*.log", handler)
    watch_directory(str(tmp_path))
    f = tmp_path / "test.log"
    unregister_callback(cid)
    f.write_text("log")
    time.sleep(0.3)
    assert not events

def test_priority_order(tmp_path):
    set_polling_strategy(lambda: 0.1)
    order = []
    def handler1(ev):
        order.append("h1")
    def handler2(ev):
        order.append("h2")
    register_callback("*.txt", handler2, priority=0)
    register_callback("*.txt", handler1, priority=1)
    watch_directory(str(tmp_path))
    f = tmp_path / "p.txt"
    f.write_text("p")
    time.sleep(0.3)
    assert order == ["h1", "h2"]

def test_rate_limit(tmp_path):
    set_polling_strategy(lambda: 0.1)
    calls = []
    def handler(ev):
        calls.append(ev)
    hid = register_callback("*.dat", handler)
    configure_rate_limit(handler_id=hid, max_events_per_sec=1)
    watch_directory(str(tmp_path))
    f1 = tmp_path / "1.dat"; f1.write_text("1")
    f2 = tmp_path / "2.dat"; f2.write_text("2")
    f3 = tmp_path / "3.dat"; f3.write_text("3")
    time.sleep(0.3)
    assert len(calls) <= 1

def test_generate_change_summary(tmp_path):
    set_polling_strategy(lambda: 0.1)
    def handler(ev):
        pass
    register_callback("*.sum", handler)
    watch_directory(str(tmp_path))
    f = tmp_path / "a.sum"; f.write_text("x")
    time.sleep(0.3)
    summary = generate_change_summary(1)
    assert "1 created" in summary

@pytest.mark.asyncio
async def test_async_watcher(tmp_path):
    set_polling_strategy(lambda: 0.1)
    q = get_async_watcher()
    watch_directory(str(tmp_path))
    f = tmp_path / "async.txt"
    f.write_text("async")
    ev = await asyncio.wait_for(q.get(), timeout=1.0)
    assert isinstance(ev, FileEvent)
    assert ev.event_type == 'created'

def test_retry_policy(tmp_path):
    set_polling_strategy(lambda: 0.1)
    attempts = []
    def handler(ev):
        attempts.append(1)
        if len(attempts) < 2:
            raise ValueError("fail")
    set_retry_policy(max_retries=2, backoff_strategy='linear')
    register_callback("*.retry", handler)
    watch_directory(str(tmp_path))
    f = tmp_path / "r.retry"; f.write_text("r")
    time.sleep(0.5)
    assert len(attempts) == 2

def test_configure_logging():
    # simply ensure no errors
    configure_logging(level=logging.DEBUG)

def test_set_polling_strategy_callable(tmp_path):
    called = []
    def poller():
        called.append(1)
        return 0.05
    set_polling_strategy(poller)
    watch_directory(str(tmp_path))
    time.sleep(0.2)
    assert called

