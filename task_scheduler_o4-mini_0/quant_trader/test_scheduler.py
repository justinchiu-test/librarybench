import pytest
import datetime
import os
import time
import tempfile
from scheduler import Scheduler

def test_event_triggering():
    sched = Scheduler()
    results = []
    sched.add_event_trigger("data", lambda x: results.append(x))
    sched.trigger_event("data", {"price": 100})
    assert results == [{"price": 100}]

def test_run_in_thread():
    sched = Scheduler()
    results = []
    def work(x):
        results.append(x)
    th = sched.run_in_thread(work, 5)
    th.join(timeout=1)
    assert results == [5]

def test_calendar_exclusions_dates_and_functions():
    sched = Scheduler()
    # exclude specific date
    d = datetime.date(2022, 1, 1)
    sched.set_calendar_exclusions(d)
    assert sched.is_excluded(d)
    # exclude weekends
    def weekend(dt):
        return dt.weekday() >= 5
    sched.set_calendar_exclusions(weekend)
    assert sched.is_excluded(datetime.date(2023, 1, 7))  # Saturday
    assert not sched.is_excluded(datetime.date(2023, 1, 4))  # Wednesday

def test_send_notification():
    sched = Scheduler()
    sched.send_notification("sms", "Alert!")
    sched.send_notification("email", "Hello")
    assert ("sms", "Alert!") in sched.notifications
    assert ("email", "Hello") in sched.notifications

def test_concurrency_limits():
    sched = Scheduler()
    limit = 2
    call_count = 0
    import threading

    @sched.set_concurrency_limits("test", limit)
    def task(i, results):
        time.sleep(0.01)
        results.append(i)
    results = []
    threads = [threading.Thread(target=task, args=(i, results)) for i in range(5)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()
    assert sorted(results) == list(range(5))

def test_health_checks():
    sched = Scheduler()
    sched.register_health_check("ok", lambda: True)
    sched.register_health_check("bad", lambda: (_ for _ in ()).throw(Exception("fail")))
    status = sched.get_health_status()
    assert status["ok"] is True
    assert status["bad"] is False

def test_persist_and_load_job(tmp_path):
    db_file = tmp_path / "jobs.db"
    sched = Scheduler(str(db_file))
    meta = {"a": 1, "b": "test"}
    sched.persist_job("job1", meta)
    loaded = sched.load_job("job1")
    assert loaded == meta
    with pytest.raises(KeyError):
        sched.load_job("nonexistent")

def test_priority_queue():
    sched = Scheduler()
    sched.enqueue_job(5, "low")
    sched.enqueue_job(1, "high")
    assert sched.dequeue_job() == "high"
    assert sched.dequeue_job() == "low"
    assert sched.dequeue_job() is None

def test_get_next_run_skips_weekends_and_exclusions():
    sched = Scheduler()
    # exclude tomorrow
    tomorrow = datetime.date.today() + datetime.timedelta(days=1)
    sched.set_calendar_exclusions(tomorrow)
    # pick a time
    t = datetime.time(9, 30)
    next_run = sched.get_next_run(t, after=datetime.datetime.combine(datetime.date.today(), datetime.time(10,0)))
    # It should be day after tomorrow if tomorrow is excluded or weekend
    dr = next_run.date()
    assert dr != tomorrow
    assert next_run.time() == t

def test_dynamic_reload(tmp_path):
    cfg = tmp_path / "cfg.txt"
    cfg.write_text("v1")
    sched = Scheduler()
    calls = []
    def cb():
        calls.append(time.time())
    watcher = sched.enable_dynamic_reload(str(cfg), cb, interval=0.1)
    time.sleep(0.2)
    # modify file
    cfg.write_text("v2")
    time.sleep(0.2)
    assert len(calls) >= 2  # at least initial and change
    # we can't reliably stop the thread; just ensure callback called

