import os
import time
import threading
import json
import tempfile
import logging
import pytest
from datetime import datetime, timedelta

import devops_admin.scheduler

def test_schedule_and_list_jobs(tmp_path):
    # use a fresh scheduler
    f = tmp_path / "jobs.json"
    sch = scheduler.Scheduler(persist_file=str(f))
    def job_fn(): pass
    sch.schedule_recurring_job("job1", job_fn, 10, tags=["prod"])
    jobs = sch.list_jobs()
    assert len(jobs) == 1
    job = jobs[0]
    assert job["name"] == "job1"
    assert job["last_exit_code"] is None
    assert job["run_count"] == 0
    assert job["tags"] == ["prod"]
    # next_run approximately now + 10s
    nr = job["next_run"]
    assert isinstance(nr, datetime)
    diff = (nr - datetime.utcnow()).total_seconds()
    assert 9 <= diff <= 11

def test_persist_and_load_jobs(tmp_path):
    f = tmp_path / "jobs2.json"
    sch1 = scheduler.Scheduler(persist_file=str(f))
    def job_fn(): pass
    sch1.schedule_recurring_job("jobA", job_fn, 5, tags=["stag"])
    sch1.persist_jobs()
    # create new scheduler to load
    sch2 = scheduler.Scheduler(persist_file=str(f))
    jobs = sch2.list_jobs()
    assert len(jobs) == 1
    job = jobs[0]
    assert job["name"] == "jobA"
    assert job["run_count"] == 0
    assert job["tags"] == ["stag"]
    nr = job["next_run"]
    assert isinstance(nr, datetime)

def test_adjust_interval(tmp_path):
    sch = scheduler.Scheduler(persist_file=str(tmp_path/"j.json"))
    def fn(): pass
    sch.schedule_recurring_job("x", fn, 10)
    sch.adjust_interval("x", 20)
    job = sch.jobs["x"]
    assert job["interval"] == 20
    diff = (job["next_run"] - datetime.utcnow()).total_seconds()
    assert 19 <= diff <= 21

def test_register_hooks_and_run_job(tmp_path):
    sch = scheduler.Scheduler(persist_file=str(tmp_path/"j.json"))
    events = []
    def fn():
        events.append("run")
    sch.schedule_recurring_job("hjob", fn, 1)
    # before leader, run_job does nothing
    sch.run_job("hjob")
    assert events == []
    sch.coordinate_leader_election()
    def pre(): events.append("pre")
    def post(): events.append("post")
    sch.register_hook("hjob", "pre", pre)
    sch.register_hook("hjob", "post", post)
    sch.run_job("hjob")
    assert events == ["pre", "run", "post"]
    job = sch.jobs["hjob"]
    assert job["last_exit_code"] == 0
    assert job["run_count"] == 1

def test_run_async_job_executes_and_logs(tmp_path):
    sch = scheduler.Scheduler(persist_file=str(tmp_path/"j.json"))
    result = {}
    def job(x):
        time.sleep(0.1)
        result['v'] = x
    t = sch.run_async_job(job, 42)
    t.join(1)
    assert result.get('v') == 42

def test_coordinate_leader_election_flag(tmp_path):
    sch = scheduler.Scheduler(persist_file=str(tmp_path/"j.json"))
    assert not sch.leader
    sch.coordinate_leader_election()
    assert sch.leader

def test_graceful_shutdown_waits_and_persists(tmp_path):
    f = tmp_path / "jobs3.json"
    sch = scheduler.Scheduler(persist_file=str(f))
    # start a long-running async job
    def long_job():
        time.sleep(0.2)
    sch.run_async_job(long_job)
    sch.schedule_recurring_job("j4", lambda: None, 1)
    sch.coordinate_leader_election()
    sch.graceful_shutdown(timeout_seconds=0.1)
    # threads should be joined up to timeout
    # jobs should be persisted
    with open(str(f)) as fd:
        data = json.load(fd)
    assert "j4" in data

def test_expose_metrics(tmp_path):
    sch = scheduler.Scheduler(persist_file=str(tmp_path/"jm.json"))
    sch.coordinate_leader_election()
    def ok(): pass
    def err(): raise Exception("fail")
    sch.schedule_recurring_job("m1", ok, 1)
    sch.schedule_recurring_job("m2", err, 1)
    sch.run_job("m1")
    sch.run_job("m2")
    metrics = sch.expose_metrics()
    assert "m1" in metrics["job_success_total"]
    assert metrics["job_success_total"]["m1"] == 1
    assert metrics["job_failure_total"]["m2"] == 1
    assert "job_queue_latency_seconds" in metrics

def test_attach_logger(tmp_path):
    sch = scheduler.Scheduler(persist_file=str(tmp_path/"j.json"))
    custom = logging.getLogger("custom")
    sch.attach_logger(custom)
    assert sch.logger is custom

def test_list_jobs_empty(tmp_path):
    sch = scheduler.Scheduler(persist_file=str(tmp_path/"j.json"))
    assert sch.list_jobs() == []

def test_register_hook_invalid_when(tmp_path):
    sch = scheduler.Scheduler(persist_file=str(tmp_path/"j.json"))
    with pytest.raises(ValueError):
        sch.register_hook("any", "middle", lambda: None)
