import pytest
import time
import datetime
import os
import threading
import tempfile
import logging
import asyncio
from data_engineer.scheduler.scheduler import Scheduler

def test_schedule_and_run_sync_job(tmp_path):
    scheduler = Scheduler(persist_path=str(tmp_path / "jobs.db"))
    counter = {'count': 0}
    def job_fn():
        counter['count'] += 1
    job_id = scheduler.schedule_recurring_job(job_fn, interval=0.5)
    time.sleep(1.3)
    scheduler.graceful_shutdown()
    assert counter['count'] >= 2
    jobs = scheduler.list_jobs()
    assert any(j['id'] == job_id for j in jobs)
    assert any(j['count'] >= 2 for j in jobs if j['id'] == job_id)

@pytest.mark.asyncio
async def test_async_job(tmp_path):
    scheduler = Scheduler(persist_path=str(tmp_path / "jobs.db"))
    counter = {'count': 0}
    async def job_fn():
        await asyncio.sleep(0.1)
        counter['count'] += 1
    job_id = scheduler.schedule_recurring_job(job_fn, interval=0.5)
    await asyncio.sleep(1.3)
    scheduler.graceful_shutdown()
    assert counter['count'] >= 2

def test_metrics_exposure(tmp_path):
    scheduler = Scheduler(persist_path=str(tmp_path / "jobs.db"))
    def good():
        pass
    def bad():
        raise RuntimeError("fail")
    gid = scheduler.schedule_recurring_job(good, 0.5)
    bid = scheduler.schedule_recurring_job(bad, 0.5)
    time.sleep(1.3)
    scheduler.graceful_shutdown()
    metrics = scheduler.expose_metrics()
    assert f'job_runs_total{{job_id="{gid}"}}' in metrics
    assert f'job_failures_total{{job_id="{bid}"}}' in metrics
    assert 'job_latency_seconds_count' in metrics

def test_hooks(tmp_path):
    scheduler = Scheduler(persist_path=str(tmp_path / "jobs.db"))
    events = []
    def on_start(job_id):
        events.append(('start', job_id))
    def on_success(job_id):
        events.append(('success', job_id))
    def on_failure(job_id, exc):
        events.append(('failure', job_id, str(exc)))
    scheduler.register_hook('start', on_start)
    scheduler.register_hook('success', on_success)
    scheduler.register_hook('failure', on_failure)
    def good():
        pass
    def bad():
        raise ValueError("err")
    gid = scheduler.schedule_recurring_job(good, 0.5)
    bid = scheduler.schedule_recurring_job(bad, 0.5)
    time.sleep(1.3)
    scheduler.graceful_shutdown()
    # expect at least one of each
    assert any(e[0]=='start' and e[1]==gid for e in events)
    assert any(e[0]=='success' and e[1]==gid for e in events)
    assert any(e[0]=='failure' and e[1]==bid for e in events)

def test_persistence(tmp_path):
    dbfile = str(tmp_path / "jobs.db")
    scheduler = Scheduler(persist_path=dbfile)
    def job_fn():
        pass
    jid = scheduler.schedule_recurring_job(job_fn, 0.2)
    time.sleep(0.3)
    scheduler.graceful_shutdown()
    # restart scheduler
    scheduler2 = Scheduler(persist_path=dbfile)
    jobs = scheduler2.list_jobs()
    assert any(j['id']==jid for j in jobs)
    job_meta = next(j for j in jobs if j['id']==jid)
    assert job_meta['count'] >= 1

def test_adjust_interval(tmp_path):
    scheduler = Scheduler(persist_path=str(tmp_path / "jobs.db"))
    counter = {'count':0}
    def job_fn():
        counter['count'] +=1
    jid = scheduler.schedule_recurring_job(job_fn, 1)
    time.sleep(1.1)
    scheduler.adjust_interval(jid, 0.3)
    time.sleep(0.7)
    scheduler.graceful_shutdown()
    assert counter['count'] >= 3

def test_leader_election(tmp_path):
    lockfile = str(tmp_path / "leader.lock")
    s1 = Scheduler(persist_path=str(tmp_path/"a.db"), leader_lock_file=lockfile)
    s2 = Scheduler(persist_path=str(tmp_path/"b.db"), leader_lock_file=lockfile)
    first = s1.coordinate_leader_election()
    second = s2.coordinate_leader_election()
    assert first != second
    assert first is True
    assert second is False
    s1.graceful_shutdown()
    # after releasing, s2 can acquire
    acquired_after = s2.coordinate_leader_election()
    assert acquired_after

def test_logging(tmp_path):
    scheduler = Scheduler(persist_path=str(tmp_path / "jobs.db"))
    log_records = []
    class H(logging.Handler):
        def emit(self, record):
            log_records.append(record)
    handler = H()
    scheduler.attach_logger(handler)
    def bad():
        raise RuntimeError("logfail")
    jid = scheduler.schedule_recurring_job(bad, 0.5)
    time.sleep(0.6)
    scheduler.graceful_shutdown()
    assert any("Job" in rec.getMessage() for rec in log_records)

def test_graceful_shutdown_waits(tmp_path):
    scheduler = Scheduler(persist_path=str(tmp_path / "jobs.db"))
    order = []
    def long_job():
        order.append('start')
        time.sleep(0.5)
        order.append('end')
    jid = scheduler.schedule_recurring_job(long_job, 1)
    time.sleep(0.1)
    # trigger shutdown while job running
    t = threading.Thread(target=scheduler.graceful_shutdown)
    t.start()
    t.join(timeout=1.0)
    # ensure job finished before shutdown
    assert order == ['start', 'end']
