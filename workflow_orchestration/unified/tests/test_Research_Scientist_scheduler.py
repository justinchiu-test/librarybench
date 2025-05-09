import time
import pytest
from workflow.scheduler import Scheduler
from workflow.manager import TaskManager
from workflow.models import Task, RetryPolicy, TaskState

def test_scheduler_runs_due_tasks(monkeypatch):
    manager = TaskManager()
    # dummy task
    def f():
        return 'ok'
    task = Task(id='sched1', func=f, args=(), priority=1,
                retry_policy=RetryPolicy())
    scheduler = Scheduler()
    # pretend time.time: start at 100
    fake_time = [100.0]
    def time_time():
        return fake_time[0]
    monkeypatch.setattr(time, 'time', time_time)
    scheduler.schedule(manager, task, interval_seconds=10)
    # first run_pending at t=100: not due
    scheduler.run_pending()
    assert manager.get_task('sched1') is None
    # advance time to 110
    fake_time[0] = 110.0
    scheduler.run_pending()
    # should have scheduled the task
    t = manager.get_task('sched1')
    assert t is not None
    assert t.state == TaskState.PENDING
