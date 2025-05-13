import threading
import time
from datetime import datetime, timedelta, timezone
import pytest
from scheduler import Scheduler

def test_register_and_run_one_off_task():
    sched = Scheduler()
    result = []
    run_time = datetime.now(timezone.utc) + timedelta(seconds=1)
    def job():
        result.append("ran")
    sched.register_task("t1", job, one_off=run_time)
    sched.start()
    time.sleep(1.1)
    sched.run_pending()
    assert result == ["ran"]
    # ensure it does not run again
    time.sleep(1)
    sched.run_pending()
    assert result == ["ran"]
    assert sched.get_task_state("t1") == "completed"

def test_interval_task_and_dynamic_reschedule():
    sched = Scheduler()
    result = []
    def job():
        result.append("tick")
    sched.register_task("t2", job, interval=0.5)
    sched.start()
    time.sleep(0.6)
    sched.run_pending()
    assert result == ["tick"]
    # reschedule to 0.2s
    sched.dynamic_reschedule("t2", interval=0.2)
    time.sleep(0.25)
    sched.run_pending()
    assert result == ["tick", "tick"]
    assert sched.get_task_state("t2") == "completed" or sched.get_task_state("t2") == "pending"

def test_cron_expression_support():
    sched = Scheduler()
    result = []
    # every minute => we treat as 60s, but override to 0 seconds for test via cron 0th minute
    now = datetime.now(timezone.utc)
    expr = f"{now.minute} * * * *"
    def job():
        result.append("cron")
    sched.register_task("t3", job, cron=expr)
    sched.start()
    time.sleep(0.1)
    sched.run_pending()
    # since schedule is next hour or next in <60s, may or may not run; ensure next_run updated
    nr = sched.get_next_run("t3")
    assert isinstance(nr, datetime)

def test_dependencies_and_priority():
    sched = Scheduler()
    run_order = []
    def preproc():
        run_order.append("pre")
    def train():
        run_order.append("train")
    def validate():
        run_order.append("val")
    sched.register_task("pre", preproc, interval=0.1)
    sched.register_task("train", train, interval=0.1, dependencies=["pre"])
    sched.register_task("val", validate, interval=0.1, dependencies=["train"], priority=5)
    sched.start()
    time.sleep(0.15)
    sched.run_pending()
    # pre should run first, then train, then val
    assert run_order == ["pre", "train", "val"]

def test_pause_resume_cancel():
    sched = Scheduler()
    result = []
    def job():
        result.append(1)
    sched.register_task("t4", job, interval=0.1)
    sched.start()
    sched.pause_task("t4")
    time.sleep(0.15)
    sched.run_pending()
    assert result == []
    sched.resume_task("t4")
    time.sleep(0.15)
    sched.run_pending()
    assert result == [1]
    sched.cancel_task("t4")
    time.sleep(0.15)
    sched.run_pending()
    assert result == [1]

def test_pre_post_hooks():
    sched = Scheduler()
    order = []
    def job():
        order.append("job")
    def pre():
        order.append("pre")
    def post():
        order.append("post")
    sched.register_task("t5", job, interval=0.1)
    sched.register_pre_post_hooks("t5", [pre], [post])
    sched.start()
    time.sleep(0.15)
    sched.run_pending()
    assert order == ["pre", "job", "post"]

def test_timezone_awareness():
    sched = Scheduler()
    result = []
    # schedule at local timezone now + 1s
    local_dt = datetime.now(timezone.utc).astimezone() + timedelta(seconds=1)
    def job():
        result.append("tz")
    sched.register_task("tz", job, one_off=local_dt)
    sched.start()
    time.sleep(1.1)
    sched.run_pending()
    assert result == ["tz"]

def test_thread_safety_under_concurrent_registration():
    sched = Scheduler()
    def dummy():
        pass
    def reg_tasks(start, end):
        for i in range(start, end):
            sched.register_task(f"t{i}", dummy, interval=1)
    threads = []
    for i in range(5):
        t = threading.Thread(target=reg_tasks, args=(i*10, (i+1)*10))
        threads.append(t)
        t.start()
    for t in threads:
        t.join()
    # ensure all tasks registered
    assert len(sched.tasks) == 50
