import threading
import time
from datetime import datetime, timedelta, timezone
import pytest
from scheduler import (
    Scheduler,
    TaskStatus,
    example_k8s_rolling_update,
    example_docker_image_sweep,
    example_cloud_snapshot,
)

def test_one_off_execution():
    sched = Scheduler()
    results = []
    def job():
        results.append("run")
    run_at = datetime.now(timezone.utc) + timedelta(seconds=1)
    tid = sched.add_task(job, run_at=run_at)
    time.sleep(1.1)
    sched.run_pending()
    assert results == ["run"]
    assert sched.tasks[tid].status == TaskStatus.COMPLETED

def test_cron_next_run():
    sched = Scheduler()
    def job(): pass
    # Every minute
    tid = sched.add_task(job, cron_expr="* * * * *")
    t = sched.tasks[tid]
    assert t.next_run is not None
    now = datetime.now(timezone.utc)
    assert t.next_run > now

def test_dependencies_and_order():
    sched = Scheduler()
    results = []
    def job1():
        results.append("first")
    def job2():
        results.append("second")
    now = datetime.now(timezone.utc)
    tid1 = sched.add_task(job1, run_at=now)
    tid2 = sched.add_task(job2, run_at=now)
    sched.add_dependency(tid2, tid1)
    sched.run_pending()
    assert results == ["first", "second"]

def test_priority_order():
    sched = Scheduler()
    results = []
    def job_low():
        results.append("low")
    def job_high():
        results.append("high")
    now = datetime.now(timezone.utc)
    tid1 = sched.add_task(job_low, run_at=now, priority=1)
    tid2 = sched.add_task(job_high, run_at=now, priority=10)
    sched.run_pending()
    assert results == ["high", "low"]

def test_pause_and_resume():
    sched = Scheduler()
    results = []
    def job():
        results.append("x")
    run_at = datetime.now(timezone.utc)
    tid = sched.add_task(job, run_at=run_at)
    sched.pause_task(tid)
    sched.run_pending()
    assert results == []
    assert sched.tasks[tid].status == TaskStatus.PAUSED
    sched.resume_task(tid)
    sched.run_pending()
    assert results == ["x"]

def test_cancel():
    sched = Scheduler()
    results = []
    def job():
        results.append("y")
    run_at = datetime.now(timezone.utc)
    tid = sched.add_task(job, run_at=run_at)
    sched.cancel_task(tid)
    sched.run_pending()
    assert results == []
    assert sched.tasks[tid].status == TaskStatus.CANCELED

def test_dynamic_reschedule():
    sched = Scheduler()
    results = []
    def job():
        results.append("d")
    run_at = datetime.now(timezone.utc) + timedelta(seconds=5)
    tid = sched.add_task(job, run_at=run_at)
    # move sooner
    new_time = datetime.now(timezone.utc) + timedelta(seconds=1)
    sched.reschedule_task(tid, run_at=new_time)
    time.sleep(1.1)
    sched.run_pending()
    assert results == ["d"]

def test_pre_and_post_hooks():
    sched = Scheduler()
    order = []
    def job():
        order.append("job")
    def pre(task):
        order.append("pre")
    def post(task):
        order.append("post")
    run_at = datetime.now(timezone.utc)
    tid = sched.add_task(job, run_at=run_at)
    sched.register_pre_hook(tid, pre)
    sched.register_post_hook(tid, post)
    sched.run_pending()
    assert order == ["pre", "job", "post"]

def test_timezone_awareness():
    sched = Scheduler()
    def job(): pass
    # Schedule one-off in US/Eastern timezone for now + 1 sec
    est = timezone(timedelta(hours=-5))
    run_at_est = datetime.now(est) + timedelta(seconds=1)
    tid = sched.add_task(job, run_at=run_at_est, tz="America/New_York")
    t = sched.tasks[tid]
    # next_run should be in UTC and roughly 1 second ahead
    now = datetime.now(timezone.utc)
    assert t.next_run > now
    time.sleep(1.1)
    # no-op run to check no errors
    sched.run_pending()

def test_thread_safety():
    sched = Scheduler()
    def dummy():
        pass
    def worker():
        for _ in range(100):
            sched.add_task(dummy, run_at=datetime.now(timezone.utc))
    threads = [threading.Thread(target=worker) for _ in range(5)]
    for th in threads: th.start()
    for th in threads: th.join()
    # Expect 500 tasks
    assert len(sched.tasks) == 500

def test_documentation_examples():
    # just ensure example functions exist
    example_k8s_rolling_update()
    example_docker_image_sweep()
    example_cloud_snapshot()
