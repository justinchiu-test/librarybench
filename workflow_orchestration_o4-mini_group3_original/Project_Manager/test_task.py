import time
import pytest
from Project_Manager.core.task import Task, TaskStatus

def test_task_success():
    t = Task("t1", func=lambda: 1+1, timeout=2)
    status = t.execute({})
    assert status == TaskStatus.SUCCESS
    assert t.attempts == 1
    assert t.duration() >= 0

def test_task_timeout():
    def long_task():
        time.sleep(0.2)
    t = Task("t2", func=long_task, timeout=0.1, max_retries=1, retry_delay_seconds=0)
    status = t.execute({})
    assert status == TaskStatus.FAILED
    # 2 attempts: initial + retry
    assert t.attempts == 2

def test_task_exception_and_retry():
    call_count = {"n": 0}
    def flaky():
        call_count["n"] += 1
        if call_count["n"] < 2:
            raise ValueError("fail")
        return "ok"
    t = Task("t3", func=flaky, timeout=1, max_retries=2, retry_delay_seconds=0)
    status = t.execute({})
    assert status == TaskStatus.SUCCESS
    assert t.attempts == 2

def test_task_no_retry_on_success():
    t = Task("t4", func=lambda: "good", timeout=1, max_retries=5, retry_delay_seconds=0)
    status = t.execute({})
    assert status == TaskStatus.SUCCESS
    assert t.attempts == 1
