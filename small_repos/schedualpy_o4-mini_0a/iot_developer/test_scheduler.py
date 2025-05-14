import datetime
import time
from scheduler.scheduler import Scheduler

def test_schedule_and_next_run_no_jitter():
    sched = Scheduler()
    def job(): pass
    sched.schedule("job1", job, cron_interval_seconds=10, jitter_seconds=0)
    before = datetime.datetime.utcnow()
    next_run = sched.next_run("job1")
    assert isinstance(next_run, datetime.datetime)
    delta = (next_run - before).total_seconds()
    assert 9.9 <= delta <= 10.1  # allow small drift

def test_schedule_and_next_run_with_jitter():
    sched = Scheduler()
    def job(): pass
    sched.schedule("job2", job, cron_interval_seconds=5, jitter_seconds=3)
    last = datetime.datetime.utcnow()
    next_run = sched.next_run("job2", last_run=last)
    delta = (next_run - last).total_seconds()
    assert 5 <= delta <= 8

def test_missing_job_raises():
    sched = Scheduler()
    import pytest
    with pytest.raises(KeyError):
        sched.next_run("unknown")
