import time
import pytest
from DevOpsEngineer.tasks.manager import Task, TaskManager
from DevOpsEngineer.tasks.exceptions import TaskTimeoutError, TaskExecutionError

def test_simple_success():
    def work(ctx, inputs):
        return {"result": inputs["value"] * 2}

    tm = TaskManager()
    t = Task(name="double", func=work, inputs={"value": 3})
    tm.add_task(t)
    results = tm.run_all()
    assert results["double"] == {"result": 6}
    meta = tm.metadata["double"]
    assert meta.status.value == "SUCCESS"
    assert meta.attempts == 1
    assert meta.error is None

def test_simple_failure_no_retry():
    def bad(ctx, inputs):
        raise RuntimeError("fail")

    tm = TaskManager()
    t = Task(name="bad", func=bad, max_retries=0)
    tm.add_task(t)
    results = tm.run_all()
    assert "bad" not in results
    meta = tm.metadata["bad"]
    assert meta.status.value == "FAILURE"
    assert meta.attempts == 1
    assert isinstance(meta.error, TaskExecutionError)

def test_retry_success():
    def flaky(ctx, inputs):
        count = ctx.get("fails", 0)
        if count < inputs.get("fails", 1):
            ctx.set("fails", count + 1)
            raise ValueError("flaky")
        return {"ok": True}

    tm = TaskManager()
    t = Task(name="flaky", func=flaky, inputs={"fails": 2}, max_retries=3, retry_delay_seconds=0.01, backoff=False)
    tm.add_task(t)
    start = time.time()
    results = tm.run_all()
    elapsed = time.time() - start
    # should have retried twice then succeed
    assert results["flaky"] == {"ok": True}
    meta = tm.metadata["flaky"]
    assert meta.status.value == "SUCCESS"
    assert meta.attempts == 3  # 2 fails + 1 success
    assert elapsed >= 0.02  # at least two delays
    assert meta.error is None

def test_retry_exhausted():
    def always_fail(ctx, inputs):
        raise RuntimeError("nope")

    tm = TaskManager()
    t = Task(name="always", func=always_fail, max_retries=2, retry_delay_seconds=0.0)
    tm.add_task(t)
    tm.run_all()
    meta = tm.metadata["always"]
    assert meta.status.value == "FAILURE"
    assert meta.attempts == 3  # 1 initial + 2 retries
    assert isinstance(meta.error, TaskExecutionError)

def test_timeout():
    def slow(ctx, inputs):
        time.sleep(0.1)
        return {}

    tm = TaskManager()
    t = Task(name="slow", func=slow, timeout_seconds=0.01, max_retries=1, retry_delay_seconds=0.0)
    tm.add_task(t)
    tm.run_all()
    meta = tm.metadata["slow"]
    assert meta.status.value == "FAILURE"
    assert meta.attempts == 2  # initial + one retry
    assert isinstance(meta.error, TaskTimeoutError)
