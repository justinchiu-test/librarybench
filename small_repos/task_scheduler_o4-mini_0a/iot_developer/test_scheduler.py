import os
import tempfile
import datetime
import threading
import time
import json
import pytest
from scheduler import Scheduler, ZoneInfo

def test_track_job_stats(tmp_path):
    db = str(tmp_path / "stats.db")
    sched = Scheduler(db_path=db)
    sched.trackJobStats("job1", True, "ok")
    sched.trackJobStats("job1", False, "fail")
    stats = sched.stats["job1"]
    assert stats['runs'] == 2
    assert stats['success'] == 1
    assert stats['fail'] == 1
    assert stats['last_log'] == "fail"
    # reload
    sched2 = Scheduler(db_path=db)
    stats2 = sched2.stats["job1"]
    assert stats2 == stats

def test_set_timezone():
    sched = Scheduler()
    sched.setTimezone("g1", "UTC")
    tz = sched.timezones["g1"]
    assert isinstance(tz, ZoneInfo)
    assert str(tz) == "UTC"

def test_event_trigger():
    sched = Scheduler()
    results = []
    def handler1(x):
        results.append(("h1", x))
    def handler2(x):
        results.append(("h2", x))
    sched.onEventTrigger("evt", handler1)
    sched.onEventTrigger("evt", handler2)
    sched.triggerEvent("evt", 42)
    assert ("h1", 42) in results
    assert ("h2", 42) in results

def test_add_tag_metadata_and_persistence(tmp_path):
    db = str(tmp_path / "jobs.db")
    sched = Scheduler(db_path=db)
    sched.addTagMetadata("jobA", {"firmware": "1.0", "region": "us"})
    assert sched.job_tags["jobA"]["firmware"] == "1.0"
    # reload
    sched2 = Scheduler(db_path=db)
    assert sched2.job_tags["jobA"]["region"] == "us"

def test_get_next_run_time():
    sched = Scheduler()
    # no interval
    assert sched.getNextRunTime("nojob") is None
    sched.addTagMetadata("job2", {"interval": 60})
    nxt = sched.getNextRunTime("job2")
    assert isinstance(nxt, datetime.datetime)
    # with last_run
    last = datetime.datetime(2020,1,1, tzinfo=datetime.timezone.utc)
    sched.job_tags["job2"]["last_run"] = last
    nxt2 = sched.getNextRunTime("job2")
    assert nxt2 == last + datetime.timedelta(seconds=60)

def test_shutdown_and_accept():
    sched = Scheduler()
    assert sched.acceptNewTasks()
    sched.shutdownGracefully()
    assert not sched.acceptNewTasks()

def test_pause_and_resume_tasks():
    sched = Scheduler()
    sched.addTagMetadata("j1", {"region": "us"})
    sched.addTagMetadata("j2", {"region": "eu"})
    sched.pauseTasks("region", "us")
    assert sched.isPaused("j1")
    assert not sched.isPaused("j2")
    sched.resumeTasks("region", "us")
    assert not sched.isPaused("j1")

def test_enable_overlap_locking():
    sched = Scheduler()
    lock = sched.enableOverlapLocking("job1")
    assert lock.acquire(blocking=False)
    lock.release()

def test_retry_strategy():
    sched = Scheduler()
    sched.setRetryConfig("job1", max_attempts=3, base_delay=2)
    for attempt in range(1, 4):
        d = sched.retryStrategy("job1", attempt)
        assert isinstance(d, float) or isinstance(d, int)
        assert d >= 0
    assert sched.retryStrategy("job1", 4) is None

def test_persistent_storage_sqlite(tmp_path):
    db = str(tmp_path / "persist.db")
    sched1 = Scheduler(db_path=db)
    sched1.addTagMetadata("jX", {"v": 100})
    sched1.trackJobStats("jX", True, "log")
    # instantiate new scheduler on same db
    sched2 = Scheduler(db_path=db)
    assert sched2.job_tags["jX"]["v"] == 100
    st = sched2.stats["jX"]
    assert st['runs'] == 1
    assert st['success'] == 1
    assert st['last_log'] == "log"
