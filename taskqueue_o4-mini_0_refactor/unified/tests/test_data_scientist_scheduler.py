import time
from datetime import datetime, timedelta
from data_scientist.ml_pipeline.scheduler import Scheduler

def test_schedule_and_cancel():
    scheduler = Scheduler()
    called = {"flag": False}
    def f(): called["flag"] = True
    job_id = scheduler.schedule(0.1, f)
    assert job_id in scheduler.jobs
    time.sleep(0.2)
    assert called["flag"] is True

def test_schedule_datetime():
    scheduler = Scheduler()
    called = {"flag": False}
    def f(): called["flag"] = True
    run_at = datetime.now() + timedelta(seconds=0.1)
    job_id = scheduler.schedule(run_at, f)
    time.sleep(0.2)
    assert called["flag"] is True

def test_cancel_job():
    scheduler = Scheduler()
    called = {"flag": False}
    def f(): called["flag"] = True
    job_id = scheduler.schedule(1, f)
    ok = scheduler.cancel(job_id)
    assert ok is True
    time.sleep(1.1)
    assert called["flag"] is False
