import time
import pytest
from task_manager.task_manager import TaskManager

def test_queue_task_success():
    tm = TaskManager(max_workers=2)
    def hello(name):
        return f"Hello {name}"
    tid = tm.queue_task(hello, args=("World",))
    # wait for completion
    time.sleep(0.2)
    meta = tm.get_task_metadata(tid)
    assert meta['status'] == 'success'
    assert meta['execution_time'] is not None
    tm.shutdown()

def test_retry_failed_then_success():
    tm = TaskManager(max_workers=1)
    state = {'count': 0}
    def sometimes_fail():
        state['count'] += 1
        if state['count'] < 2:
            raise ValueError("fail once")
        return "ok"
    tid = tm.queue_task(sometimes_fail, max_retries=1, retry_delay_seconds=0.1)
    time.sleep(0.5)
    meta = tm.get_task_metadata(tid)
    assert meta['status'] == 'success'
    assert meta['retry_count'] == 1
    tm.shutdown()

def test_retry_exhausted_sends_alert():
    tm = TaskManager(max_workers=1)
    def always_fail():
        raise RuntimeError("bad")
    tid = tm.queue_task(always_fail, max_retries=1, retry_delay_seconds=0.1)
    time.sleep(0.5)
    meta = tm.get_task_metadata(tid)
    assert meta['status'] == 'failed'
    # one retry + initial => retry_count=2, but max_retries=1 so only one retry => retry_count==1 or 2?
    # Our implementation increments retry_count on each failure
    assert meta['retry_count'] == 2
    assert any("failed after" in a for a in tm.alerts)
    tm.shutdown()

def test_timeout():
    tm = TaskManager(max_workers=1)
    def long_task():
        time.sleep(0.5)
    tid = tm.queue_task(long_task, timeout=0.1)
    time.sleep(0.3)
    meta = tm.get_task_metadata(tid)
    assert meta['status'] == 'timeout'
    assert any("timed out" in a for a in tm.alerts)
    tm.shutdown()

def test_cancel_task():
    tm = TaskManager(max_workers=1)
    def long_task():
        time.sleep(0.5)
    tid = tm.queue_task(long_task)
    time.sleep(0.1)
    ok = tm.cancel_task(tid)
    assert ok
    time.sleep(0.1)
    meta = tm.get_task_metadata(tid)
    assert meta['status'] == 'canceled'
    tm.shutdown()

def test_schedule_tasks():
    tm = TaskManager(max_workers=1)
    counter = {'n': 0}
    def inc():
        counter['n'] += 1
    sid = tm.schedule_task(inc, interval_seconds=0.1)
    time.sleep(0.35)
    # should have fired about 3 times
    assert counter['n'] >= 2
    ok = tm.cancel_schedule(sid)
    assert ok
    tm.shutdown()
