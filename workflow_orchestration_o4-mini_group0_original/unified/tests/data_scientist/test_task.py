import time
import pytest
from unified.ds.logger_config import configure_logger
from unified.ds.task_manager import Task

logger = configure_logger(log_file='test_task.log')

def test_task_success():
    def f():
        return "hello"
    task = Task("t1", f, timeout=5)
    res = task.run(logger)
    assert res == "hello"
    assert task.status == "SUCCESS"
    assert task.attempts == 1

def test_task_failure_with_retries():
    calls = {"count": 0}
    def f():
        calls["count"] += 1
        raise ValueError("oops")
    task = Task("t2", f, timeout=5, max_retries=2, retry_delay_seconds=0)
    with pytest.raises(Exception) as exc:
        task.run(logger)
    assert "oops" in str(exc.value)
    assert task.attempts == 3

def test_task_timeout():
    def f():
        time.sleep(2)
        return 1
    task = Task("t3", f, timeout=1, max_retries=0)
    with pytest.raises(Exception) as exc:
        task.run(logger)
    assert "Timeout" in str(exc.value)
    assert task.status == "FAILED"

def test_task_backoff_delay():
    timestamps = []
    def f():
        timestamps.append(time.time())
        if len(timestamps) < 2:
            raise RuntimeError("fail")
        return "ok"
    task = Task("t4", f, timeout=5,
                max_retries=1,
                retry_delay_seconds=1,
                backoff_factor=2)
    start = time.time()
    res = task.run(logger)
    end = time.time()
    assert res == "ok"
    assert task.attempts == 2
    assert (end - start) >= 1  # at least one second backoff