import threading
import datetime
import time
import os
import tempfile
import sqlite3
import pytest
from scheduler.scheduler import Scheduler

def test_add_event_trigger_and_storage():
    sched = Scheduler()
    def cb(): pass
    sched.add_event_trigger('git_commit', cb)
    assert ('git_commit', cb) in sched.triggers
    with pytest.raises(ValueError):
        sched.add_event_trigger('bad', 123)

def test_run_in_thread_executes_function():
    sched = Scheduler()
    result = {'ran': False}
    def fn(x):
        time.sleep(0.1)
        result['ran'] = x
    t = sched.run_in_thread(fn, True)
    assert isinstance(t, threading.Thread)
    t.join(timeout=1)
    assert result['ran'] is True
    with pytest.raises(ValueError):
        sched.run_in_thread(123)

def test_set_calendar_exclusions_and_validation():
    sched = Scheduler()
    today = datetime.date.today()
    dt = datetime.datetime.now()
    sched.set_calendar_exclusions([today, dt])
    assert today in sched.exclusions
    assert dt.date() in sched.exclusions
    with pytest.raises(ValueError):
        sched.set_calendar_exclusions(['not a date'])

def test_send_notification_and_storage():
    sched = Scheduler()
    sched.send_notification('slack', 'Deployed', 'success')
    assert sched.notifications == [{
        'channel': 'slack',
        'message': 'Deployed',
        'event': 'success'
    }]
    with pytest.raises(ValueError):
        sched.send_notification('', 'msg', 'evt')
    with pytest.raises(ValueError):
        sched.send_notification('ch', '', 'evt')
    with pytest.raises(ValueError):
        sched.send_notification('ch', 'msg', '')

def test_set_concurrency_limits_and_validation():
    sched = Scheduler()
    sched.set_concurrency_limits(5, {'jobA': 2, 'jobB': 1})
    assert sched.global_concurrency == 5
    assert sched.job_concurrency == {'jobA': 2, 'jobB': 1}
    sched2 = Scheduler()
    with pytest.raises(ValueError):
        sched2.set_concurrency_limits(0)
    with pytest.raises(ValueError):
        sched2.set_concurrency_limits(2, per_job_limits='bad')

def test_register_health_check_and_invocation():
    sched = Scheduler()
    def check(): return {'status': 'ok'}
    sched.register_health_check('hc1', check)
    assert 'hc1' in sched.health_checks
    assert sched.health_checks['hc1']() == {'status': 'ok'}
    with pytest.raises(ValueError):
        sched.register_health_check('hc2', 123)

def test_persist_and_load_jobs(tmp_path):
    db_file = tmp_path / "jobs.db"
    sched = Scheduler(db_url=str(db_file))
    job1 = sched.persist_jobs('backup', '0 0 * * *')
    job2 = sched.persist_jobs('deploy', '@hourly')
    assert job1 != job2
    assert job1 in sched.jobs and job2 in sched.jobs
    # New scheduler instance using same file
    sched2 = Scheduler(db_url=str(db_file))
    loaded = sched2.load_jobs()
    assert job1 in loaded and loaded[job1]['name'] == 'backup'
    assert job2 in loaded and loaded[job2]['spec'] == '@hourly'
    # validation
    with pytest.raises(ValueError):
        sched.persist_jobs('', 'spec')
    with pytest.raises(ValueError):
        sched.persist_jobs('name', '')

def test_priority_queue_ordering():
    sched = Scheduler()
    sched.set_priority_queue('job1', 1)
    sched.set_priority_queue('job2', 5)
    sched.set_priority_queue('job3', 3)
    assert sched.get_next_job() == 'job2'
    assert sched.get_next_job() == 'job3'
    assert sched.get_next_job() == 'job1'
    assert sched.get_next_job() is None
    with pytest.raises(ValueError):
        sched.set_priority_queue('job4', 'high')

def test_get_next_run_and_nonexistent():
    sched = Scheduler()
    # no jobs yet
    assert sched.get_next_run('nope') is None
    sched.persist_jobs('scan', '*/15 * * * *')
    nxt = sched.get_next_run('scan')
    assert isinstance(nxt, datetime.datetime)
    delta = nxt - datetime.datetime.now()
    assert 0 < delta.total_seconds() < 3700

def test_enable_dynamic_reload_flag():
    sched = Scheduler()
    assert not hasattr(sched, 'dynamic_reload_enabled')
    sched.enable_dynamic_reload()
    assert sched.dynamic_reload_enabled is True
