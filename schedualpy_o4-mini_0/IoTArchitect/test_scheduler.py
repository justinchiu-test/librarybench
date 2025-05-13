import pytest
from datetime import datetime, timedelta, timezone
import threading
import time

from scheduler.scheduler import Scheduler

def test_cron_schedule_next_run():
    sched = Scheduler()
    def dummy(): pass
    sched.schedule_cron('t1', dummy, '*/1 * * * *')
    nr = sched.get_next_run('t1')
    assert nr is not None
    now = datetime.now(timezone.utc)
    assert nr > now

def test_interval_schedule_next_run():
    sched = Scheduler()
    def dummy(): pass
    sched.schedule_interval('t2', dummy, interval_seconds=2)
    nr = sched.get_next_run('t2')
    now = datetime.now(timezone.utc)
    assert nr <= now + timedelta(seconds=2)
    assert nr > now

def test_one_off_schedule():
    sched = Scheduler()
    called = []
    def dummy(): called.append(True)
    run_at = datetime.now(timezone.utc) + timedelta(seconds=1)
    sched.schedule_one_off('t3', dummy, run_at)
    time.sleep(1.1)
    sched.run_pending()
    assert called == [True]
    assert sched.get_next_run('t3') is None

def test_pre_post_hooks():
    sched = Scheduler()
    log = []
    def pre(name): log.append(f"pre:{name}")
    def post(name): log.append(f"post:{name}")
    sched.register_pre_post_hooks(pre, post)
    def dummy(): log.append("run")
    run_at = datetime.now(timezone.utc)
    sched.schedule_one_off('t4', dummy, run_at)
    sched.run_pending()
    assert log == ["pre:t4","run","post:t4"]

def test_dependencies():
    sched = Scheduler()
    order = []
    def t1(): order.append('t1')
    def t2(): order.append('t2')
    sched.schedule_one_off('t1', t1, datetime.now(timezone.utc))
    sched.schedule_one_off('t2', t2, datetime.now(timezone.utc), dependencies=['t1'])
    sched.run_pending()
    # first pass only t1 runs
    assert order == ['t1']
    sched.run_pending()
    # now t2 can run
    assert order == ['t1','t2']

def test_priority_order():
    sched = Scheduler()
    order = []
    def low(): order.append('low')
    def high(): order.append('high')
    now = datetime.now(timezone.utc)
    sched.schedule_one_off('low', low, now, priority=1)
    sched.schedule_one_off('high', high, now, priority=10)
    sched.run_pending()
    assert order == ['high','low']

def test_pause_resume_cancel():
    sched = Scheduler()
    called = []
    def dummy(): called.append(True)
    sched.schedule_interval('t5', dummy, 1)
    sched.control_task_runtime('t5','pause')
    time.sleep(1.1)
    sched.run_pending()
    assert not called
    sched.control_task_runtime('t5','resume')
    time.sleep(1.1)
    sched.run_pending()
    assert called
    sched.control_task_runtime('t5','cancel')
    time.sleep(1.1)
    sched.run_pending()
    # canceled, no further runs
    assert len(called) == 1

def test_dynamic_reschedule():
    sched = Scheduler()
    called = []
    def dummy(): called.append(True)
    sched.schedule_interval('t6', dummy, 5)
    sched.dynamic_reschedule('t6', interval_seconds=1)
    time.sleep(1.1)
    sched.run_pending()
    assert called

def test_timezone_awareness():
    sched = Scheduler()
    called = []
    def dummy(): called.append(True)
    tz = timezone(timedelta(hours=2))
    run_at = datetime.now(tz) + timedelta(seconds=1)
    sched.schedule_one_off('tz', dummy, run_at, tz=tz)
    time.sleep(1.1)
    sched.run_pending()
    assert called

def test_thread_safety():
    sched = Scheduler()
    called = []
    def dummy(): called.append(True)
    sched.schedule_interval('t7', dummy, 0.5)
    def worker():
        for _ in range(5):
            sched.control_task_runtime('t7','pause')
            sched.control_task_runtime('t7','resume')
    threads = [threading.Thread(target=worker) for _ in range(5)]
    for t in threads: t.start()
    time.sleep(1)
    sched.run_pending()
    # at least one call should succeed
    assert called

def test_documentation_examples_exist():
    from scheduler.scheduler import Scheduler
    sched = Scheduler()
    assert hasattr(sched, 'example_mqtt_pipeline')
    assert hasattr(sched, 'example_edge_to_cloud_batch')
    assert hasattr(sched, 'example_autoscale_trigger')
