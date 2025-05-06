import pytest
import time
from it_manager.tasks import Task, TaskState
from it_manager.exceptions import TaskTimeoutError, MaxRetriesExceeded

def sample_success(a, b):
    return a + b

def sample_fail_once(a):
    if not hasattr(sample_fail_once, "_called"):
        sample_fail_once._called = True
        raise ValueError("fail")
    return a

def sample_long():
    time.sleep(0.2)
    return True

def test_task_success():
    t = Task(sample_success, name="add", timeout=1, max_retries=0)
    res = t.run(2,3)
    assert res == 5
    assert t.state == TaskState.SUCCESS
    assert t.attempts == 1

def test_task_retry_and_failure():
    # sample_fail_once fails first, succeeds second
    t = Task(sample_fail_once, name="f1", timeout=1, max_retries=1)
    res = t.run(10)
    assert res == 10
    assert t.attempts == 2
    # now exceed retries
    sample_fail_once._called = False
    t2 = Task(sample_fail_once, name="f2", timeout=1, max_retries=0)
    with pytest.raises(MaxRetriesExceeded):
        t2.run(5)

def test_task_timeout():
    t = Task(sample_long, name="long", timeout=0.05, max_retries=0)
    with pytest.raises(MaxRetriesExceeded):
        t.run()

def test_task_state_transitions():
    def quick():
        return "ok"
    t = Task(quick, timeout=1)
    assert t.state == TaskState.PENDING
    res = t.run()
    assert t.state == TaskState.SUCCESS
