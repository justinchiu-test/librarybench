import pytest
import time
from datetime import datetime, timedelta
from scheduler.scheduler import ThreadSafeScheduler

def test_one_off_task():
    sched = ThreadSafeScheduler()
    result = []
    def task():
        result.append('ran')
    run_at = time.time() + 0.5
    job_id = sched.schedule_one_off_task(task, run_at)
    time.sleep(1)
    assert 'ran' in result
    assert job_id not in sched.list_jobs()

def test_recurring_and_cancel():
    sched = ThreadSafeScheduler()
    count = {'runs': 0}
    def task():
        count['runs'] += 1
    job_id = sched.schedule_recurring(task, interval=0.2, sla_jitter=0)
    time.sleep(0.7)
    sched.cancel(job_id)
    assert count['runs'] >= 2
    assert job_id not in sched.list_jobs()

def test_dynamic_reschedule():
    sched = ThreadSafeScheduler()
    count = {'runs': 0}
    def task():
        count['runs'] += 1
    job_id = sched.schedule_recurring(task, interval=0.2, sla_jitter=0)
    time.sleep(0.5)
    sched.dynamic_reschedule(job_id, 0.1)
    time.sleep(0.4)
    sched.cancel(job_id)
    assert count['runs'] >= 4
