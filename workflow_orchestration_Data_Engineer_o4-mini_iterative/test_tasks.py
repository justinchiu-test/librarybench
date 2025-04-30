import time
import pytest
from pipeline.tasks import Task, TaskState

def test_task_successful_run():
    def fn():
        return 42
    task = Task("task1", fn)
    result = task.run()
    assert result == 42
    assert task.state == TaskState.SUCCESS
    assert task.retries == 0

def test_task_failure_no_retries():
    def fn():
        raise ValueError("oops")
    task = Task("task2", fn, max_retries=0)
    result = task.run()
    assert result == []
    assert task.state == TaskState.FAILURE
    assert task.retries == 1

def test_task_retries_and_backoff():
    calls = []
    def fn():
        calls.append(time.time())
        if len(calls) < 3:
            raise RuntimeError("retry")
        return "done"

    task = Task("task3", fn, max_retries=5, retry_delay_seconds=0.1)
    # First attempt
    res1 = task.run()
    assert task.state == TaskState.PENDING
    assert task.retries == 1
    next1 = task.next_run_time

    # Simulate waiting till next_run_time
    time.sleep(0.01)
    task.next_run_time = time.time() - 1
    # Second attempt
    res2 = task.run()
    assert task.state == TaskState.PENDING
    assert task.retries == 2
    # Third attempt should succeed
    task.next_run_time = time.time() - 1
    res3 = task.run()
    assert res3 == "done"
    assert task.state == TaskState.SUCCESS
    assert task.retries == 3
