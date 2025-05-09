import time
import pytest
from task_manager.task import Task

def simple_func():
    return "ok"

def fail_once(counter=[0]):
    counter[0] += 1
    if counter[0] == 1:
        raise RuntimeError("first fail")
    return "recovered"

def always_fail():
    raise ValueError("bad")

def long_task():
    time.sleep(2)
    return "done"

def test_simple_task():
    t = Task("simple", simple_func)
    assert t.run() == "ok"

def test_retry_once():
    t = Task("flaky", fail_once, max_retries=1, retry_delay_seconds=0)
    assert t.run() == "recovered"

def test_fail_no_retry():
    t = Task("fail", always_fail, max_retries=0)
    with pytest.raises(Exception):
        t.run()

def test_timeout():
    t = Task("long", long_task, timeout=0.5, max_retries=0)
    with pytest.raises(Exception):
        t.run()
