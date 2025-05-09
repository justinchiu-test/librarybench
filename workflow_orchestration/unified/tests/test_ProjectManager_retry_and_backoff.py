import pytest
import time
from project_manager.task import Task, TaskState
from project_manager.runner import TaskRunner

class Sleeper:
    def __init__(self):
        self.delays = []
    def __call__(self, seconds):
        self.delays.append(seconds)
        # don't actually sleep

def test_retry_backoff():
    sleeper = Sleeper()
    runner = TaskRunner(sleep_fn=sleeper)
    calls = {"count": 0}
    def flaky(ctx):
        calls["count"] += 1
        if calls["count"] < 3:
            raise ValueError("fail")
        return "ok"
    t = Task("flaky", flaky, max_retries=5, retry_delay_seconds=1, backoff=True)
    runner.add_task(t)
    runner.run_all()
    assert t.state == TaskState.SUCCESS
    # calls should be 3
    assert calls["count"] == 3
    # sleep delays: after attempt1 (count1->2): 1, after attempt2: 2
    assert sleeper.delays == [1, 2]
    md = runner.metadata.get("flaky")
    assert md["attempts"] == 3

def test_retry_without_backoff():
    sleeper = Sleeper()
    runner = TaskRunner(sleep_fn=sleeper)
    calls = {"count": 0}
    def flaky2(ctx):
        calls["count"] += 1
        if calls["count"] < 3:
            raise ValueError("fail")
        return "ok"
    t2 = Task("flaky2", flaky2, max_retries=5, retry_delay_seconds=0.5, backoff=False)
    runner.add_task(t2)
    runner.run_all()
    assert calls["count"] == 3
    assert sleeper.delays == [0.5, 0.5]
