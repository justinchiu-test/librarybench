import os
import time
import threading
import datetime
import json
import pytest
from scheduler import Scheduler

def test_event_trigger_and_run_in_thread():
    scheduler = Scheduler()
    result = {}

    def handler(x):
        result['value'] = x

    scheduler.add_event_trigger('test', handler)
    thread = scheduler.trigger_event('test', 123)
    assert isinstance(thread, threading.Thread)
    thread.join(timeout=1)
    assert result.get('value') == 123

def test_calendar_exclusions_and_schedule():
    scheduler = Scheduler()
    today = datetime.date.today()
    scheduler.set_calendar_exclusions([today])
    run_time = datetime.datetime.combine(today, datetime.time(12, 0))
    scheduler.schedule_event('evt', run_time)
    assert scheduler.get_next_run() is None

    tomorrow = today + datetime.timedelta(days=1)
    run_time2 = datetime.datetime.combine(tomorrow, datetime.time(12, 0))
    scheduler.schedule_event('evt2', run_time2)
    next_run = scheduler.get_next_run()
    assert next_run.date() == tomorrow

def test_send_notification():
    scheduler = Scheduler()
    scheduler.send_notification('slack', 'hello')
    scheduler.send_notification('sms', 'world')
    assert ('slack', 'hello') in scheduler.notifications
    assert ('sms', 'world') in scheduler.notifications

def test_concurrency_limits():
    scheduler = Scheduler()
    scheduler.set_concurrency_limits('job1', 1)
    running = []

    def long_job(i):
        running.append(i)
        time.sleep(0.1)
        running.remove(i)

    # Start first
    t1 = scheduler.run_in_thread(long_job, 1, job_type='job1')
    time.sleep(0.02)
    # Try second: should block until first finishes
    start = time.time()
    t2 = scheduler.run_in_thread(long_job, 2, job_type='job1')
    t1.join()
    t2.join()
    duration = time.time() - start
    assert duration >= 0.08  # blocked approx until first releases

def test_health_checks():
    scheduler = Scheduler()
    scheduler.register_health_check()
    assert scheduler.is_alive() is True
    assert scheduler.is_ready() is True

def test_persist_and_load_jobs(tmp_path):
    persist_file = tmp_path / "jobs.json"
    scheduler = Scheduler(persist_path=str(persist_file))
    future = datetime.datetime.now() + datetime.timedelta(hours=1)
    scheduler.schedule_event('a', future)
    scheduler.schedule_event('b', future + datetime.timedelta(hours=1))
    scheduler.persist_jobs()
    assert persist_file.exists()
    # load into new scheduler
    s2 = Scheduler(persist_path=str(persist_file))
    s2.load_persisted_jobs()
    nr = s2.get_next_run()
    assert nr is not None
    assert nr.date() == future.date()

def test_priority_queue_order():
    scheduler = Scheduler()
    base = datetime.datetime.now() + datetime.timedelta(minutes=1)
    scheduler.set_priority_queue('low', 1)
    scheduler.set_priority_queue('high', 10)
    scheduler.schedule_event('low', base)
    scheduler.schedule_event('high', base)
    # Internally high priority has higher -priority
    # Next run should still be base, but ordering in heap ensures high comes first if same time
    entries = list(scheduler.jobs_heap)
    # Sort by heap order manually
    sorted_entries = sorted(entries)
    # The first in sorted_entries should be high job
    first = sorted_entries[0]
    assert first[3] == 'high'

def test_get_next_run_empty():
    scheduler = Scheduler()
    assert scheduler.get_next_run() is None

def test_dynamic_reload():
    scheduler = Scheduler()
    configs1 = {'a': 1}
    configs2 = {'a': 2}
    scheduler.enable_dynamic_reload(configs1)
    assert scheduler.dynamic_reload_enabled is True
    assert scheduler.configs == configs1
    scheduler.reload_configs(configs2)
    assert scheduler.configs == configs2
