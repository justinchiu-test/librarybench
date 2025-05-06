import time
import pytest
from workflow.scheduler import Scheduler

def test_scheduler_runs_periodically(monkeypatch):
    calls = {'count': 0}
    def task_fn():
        calls['count'] += 1
    sched = Scheduler(0.1, task_fn)
    sched.start()
    time.sleep(0.35)
    sched.stop()
    assert calls['count'] >= 3  # should have run at least 3 times
