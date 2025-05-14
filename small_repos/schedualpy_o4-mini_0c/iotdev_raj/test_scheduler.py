import pytest
import threading
import time
from datetime import datetime, timedelta
from iotscheduler.scheduler import ThreadSafeScheduler

def test_one_off_task_execution():
    sched = ThreadSafeScheduler()
    result = {}
    def task(x):
        result['value'] = x
    tid = sched.schedule_one_off_task(None, delay=0.1, func=task, x=42)
    time.sleep(0.2)
    assert result.get('value') == 42
    # task should be auto removed only by cancel; here still in tasks
    assert tid in sched.tasks

def test_interval_task_and_dynamic_reschedule():
    sched = ThreadSafeScheduler()
    counter = {'count': 0}
    def task():
        counter['count'] += 1
    sched.schedule_interval("t1", 0.1, task)
    time.sleep(0.25)
    assert counter['count'] >= 2
    # reschedule to slower interval
    sched.dynamic_reschedule("t1", interval=0.5)
    c = counter['count']
    time.sleep(0.2)
    assert counter['count'] == c  # no extra run before 0.5s

def test_cancel_task():
    sched = ThreadSafeScheduler()
    counter = {'count': 0}
    def task():
        counter['count'] += 1
    tid = "to_cancel"
    sched.schedule_one_off_task(tid, delay=0.1, func=task)
    sched.cancel(tid)
    time.sleep(0.2)
    assert counter['count'] == 0
    assert tid not in sched.tasks

def test_emit_metrics():
    sched = ThreadSafeScheduler()
    # manually call emit_metrics
    sched.emit_metrics("x", 0.05, True)
    sched.emit_metrics("x", 0.10, False)
    metrics = sched.get_metrics()
    assert metrics["counters"]["x"]["success"] == 1
    assert metrics["counters"]["x"]["failure"] == 1
    assert len(metrics["histograms"]["x"]) == 2
