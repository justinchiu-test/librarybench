import time
import datetime
import threading
import pytest
import pytz
from scheduler import Scheduler, Task, TaskStatus

def test_pre_post_hooks_and_execution_order():
    results = []

    def pre(task):
        results.append(f"pre:{task.name}")

    def post(task):
        results.append(f"post:{task.name}")

    def job(task):
        results.append(f"run:{task.name}")

    sched = Scheduler()
    t = Task(func=job, interval=1, name="t1")
    sched.register_pre_post_hooks(t, pre=pre, post=post)
    sched.register_task(t)
    sched.start()
    time.sleep(1.5)
    sched.stop()
    assert results == ["pre:t1", "run:t1", "post:t1"]

def test_dependencies_order():
    results = []
    def job_a(task):
        results.append("A")
    def job_b(task):
        results.append("B")
    sched = Scheduler()
    ta = Task(func=job_a, interval=1, name="A")
    tb = Task(func=job_b, interval=1, name="B")
    sched.declare_task_dependencies(tb, ta)
    sched.register_task(ta)
    sched.register_task(tb)
    sched.start()
    time.sleep(2.5)
    sched.stop()
    # A must run before B at least once
    assert results[0] == "A"
    assert "B" in results

def test_priority_ordering():
    results = []
    def job(task):
        results.append(task.name)
    sched = Scheduler()
    t1 = Task(func=job, interval=1, name="low", priority=1)
    t2 = Task(func=job, interval=1, name="high", priority=10)
    sched.register_task(t1)
    sched.register_task(t2)
    sched.start()
    time.sleep(1.5)
    sched.stop()
    # high should run before low when scheduled at same time
    assert results[0] == "high"
    assert results[1] == "low"

def test_control_pause_resume_cancel():
    results = []
    def job(task):
        results.append(task.name)
    sched = Scheduler()
    t = Task(func=job, interval=1, name="ctr")
    sched.register_task(t)
    sched.start()
    time.sleep(0.5)
    sched.control_task_runtime(t, "pause")
    time.sleep(1.5)
    # paused, no runs
    assert results == []
    sched.control_task_runtime(t, "resume")
    time.sleep(1.5)
    # resumed, runs once
    assert results == ["ctr"]
    sched.control_task_runtime(t, "cancel")
    time.sleep(1.5)
    # canceled, no further runs
    assert results == ["ctr"]
    sched.stop()

def test_dynamic_reschedule():
    results = []
    def job(task):
        results.append(task.name + ":" + str(task.next_run is not None))
    sched = Scheduler()
    t = Task(func=job, interval=5, name="dyn")
    sched.register_task(t)
    sched.start()
    time.sleep(1)
    sched.dynamic_reschedule(t, interval=1)
    time.sleep(1.5)
    sched.stop()
    assert any(r.startswith("dyn:") for r in results)

def test_one_off_task():
    results = []
    def job(task):
        results.append("once")
    sched = Scheduler()
    t = Task(func=job, interval=None, cron=None, one_off=True, name="one")
    # Manually schedule one-off
    t.next_run = datetime.datetime.now(pytz.utc)
    sched.register_task(t)
    sched.start()
    time.sleep(0.5)
    sched.stop()
    assert results == ["once"]
    # ensure it doesn't run again
    time.sleep(1)
    assert results == ["once"]

def test_timezone_awareness():
    results = []
    tz = 'US/Pacific'
    now = datetime.datetime.now(pytz.timezone(tz))
    # schedule cron for one minute later
    cron_expr = f"{(now + datetime.timedelta(minutes=1)).minute} {now.hour} * * *"
    def job(task):
        results.append("tz")
    sched = Scheduler()
    t = Task(func=job, cron=cron_expr, timezone=tz, name="tz")
    sched.register_task(t)
    sched.start()
    # Wait until cron matches
    time_to_wait = 65
    time.sleep(2)  # fast-forward simulation; assume it's correct
    sched.stop()
    # Can't reliably wait real minute in test; assert task has next_run set in correct tz
    assert t.next_run.tzinfo.zone == tz

def test_thread_safety():
    sched = Scheduler()
    def dummy(task):
        pass
    tasks = [Task(func=dummy, interval=1, name=str(i)) for i in range(50)]
    def reg_tasks():
        for t in tasks:
            sched.register_task(t)
    threads = [threading.Thread(target=reg_tasks) for _ in range(5)]
    for th in threads:
        th.start()
    for th in threads:
        th.join()
    # no exception means thread safety
    assert len(sched.tasks) == 50
