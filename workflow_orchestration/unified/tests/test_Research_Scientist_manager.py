import pytest
import time
from workflow.manager import TaskManager
from workflow.models import Task, RetryPolicy, TaskState

# A function that fails the first two times, then succeeds
class Flaky:
    def __init__(self):
        self.count = 0

    def __call__(self, x):
        self.count += 1
        if self.count < 3:
            raise ValueError("Intermittent failure")
        return x + 1

def test_successful_task(monkeypatch):
    manager = TaskManager()
    called = []
    def f(a, b):
        called.append((a, b))
        return a + b
    task = Task(id='t1', func=f, args=(2,3), priority=1,
                retry_policy=RetryPolicy(max_retries=1, retry_delay_seconds=0))
    manager.add_task(task)
    monkeypatch.setattr(time, 'sleep', lambda x: None)
    manager.run_all()
    t = manager.get_task('t1')
    assert t.state == TaskState.SUCCESS
    assert t.result == 5
    assert called == [(2,3)]

def test_retry_and_backoff(monkeypatch):
    manager = TaskManager()
    flaky = Flaky()
    task = Task(id='t2', func=flaky, args=(5,), priority=1,
                retry_policy=RetryPolicy(max_retries=5, retry_delay_seconds=0.1))
    manager.add_task(task)
    sleep_calls = []
    def fake_sleep(sec):
        sleep_calls.append(sec)
    monkeypatch.setattr(time, 'sleep', fake_sleep)
    manager.run_all()
    t = manager.get_task('t2')
    assert t.state == TaskState.SUCCESS
    # It should have retried twice: delays 0.1, then 0.2
    assert pytest.approx(sleep_calls) == [0.1, 0.2]

def test_failure_after_retries(monkeypatch):
    manager = TaskManager()
    def always_fail(x):
        raise RuntimeError("fail")
    task = Task(id='t3', func=always_fail, args=(1,), priority=1,
                retry_policy=RetryPolicy(max_retries=2, retry_delay_seconds=0))
    manager.add_task(task)
    monkeypatch.setattr(time, 'sleep', lambda x: None)
    manager.run_all()
    t = manager.get_task('t3')
    assert t.state == TaskState.FAILURE
    assert isinstance(t.result, RuntimeError)
