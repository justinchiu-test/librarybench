import os
import threading
import tempfile
import shutil
import time
import datetime
import json
import requests
import pytest

from scheduler.scheduler import Scheduler

def test_add_event_trigger_and_run():
    sched = Scheduler()
    called = {}
    def trigger(data):
        called['data'] = data
    sched.add_event_trigger('t1', trigger)
    assert 't1' in sched.event_triggers
    # simulate trigger
    sched.event_triggers['t1']('abc')
    assert called['data'] == 'abc'
    # test run_in_thread
    results = []
    def work(x):
        results.append(x*2)
    t = sched.run_in_thread(work, 5)
    t.join(timeout=1)
    assert results == [10]

def test_calendar_exclusions_and_weekend():
    sched = Scheduler()
    today = datetime.date.today()
    # pick a weekend
    saturday = today + datetime.timedelta((5-today.weekday())%7)
    sched.set_calendar_exclusions('cal1', ['2022-01-01'])
    assert sched.is_excluded('cal1', saturday)
    assert sched.is_excluded('cal1', '2022-01-01')
    # a normal weekday not in exclusion
    monday = today + datetime.timedelta((0-today.weekday())%7)
    assert not sched.is_excluded('cal1', monday)

def test_send_notification():
    sched = Scheduler()
    sched.send_notification('slack', 'job failed')
    sched.send_notification('email', 'job success')
    assert ('slack','job failed') in sched.notifications
    assert ('email','job success') in sched.notifications

def test_concurrency_limits():
    sched = Scheduler()
    sched.set_concurrency_limits(extract=2, load=1)
    assert 'extract' in sched.semaphores
    # acquire up to limit
    assert sched.acquire_slot('extract')
    assert sched.acquire_slot('extract')
    # third should block/fail
    res = sched.acquire_slot('extract', timeout=0.1)
    assert not res
    sched.release_slot('extract')
    assert sched.acquire_slot('extract', timeout=0.1)
    sched.release_slot('extract')
    sched.release_slot('extract')

def test_register_health_check_and_endpoints():
    sched = Scheduler()
    # use ephemeral port
    port = 8001
    sched.register_health_check(port=port)
    time.sleep(0.5)
    res1 = requests.get(f'http://localhost:{port}/healthz')
    res2 = requests.get(f'http://localhost:{port}/readyz')
    assert res1.status_code == 200 and res2.status_code == 200
    # unknown path
    r = requests.get(f'http://localhost:{port}/foo')
    assert r.status_code == 404

def test_persist_jobs(tmp_path):
    sched = Scheduler()
    sched.add_event_trigger('t1', lambda x: x)
    sched.set_calendar_exclusions('cal1', ['2022-02-02'])
    sched.set_concurrency_limits(ex=1)
    # schedule a job
    rt = datetime.datetime(2023,1,1,0,0,0)
    sched.schedule_job('job1', 5, rt)
    f = tmp_path / "state.json"
    sched.persist_jobs(str(f))
    data = json.loads(f.read_text())
    assert 't1' in data['event_triggers']
    assert data['calendar_exclusions']['cal1'] == ['2022-02-02']
    assert data['concurrency_limits']['ex'] == 1
    assert data['tasks'][0][1] == rt.isoformat()

def test_priority_queue_and_next_run():
    sched = Scheduler()
    sched.set_priority_queue(True)
    now = datetime.datetime.now()
    sched.schedule_job('a', 10, now + datetime.timedelta(minutes=5))
    sched.schedule_job('b', 5, now + datetime.timedelta(minutes=2))
    next_run = sched.get_next_run()
    assert next_run['job_id'] == 'b'
    assert next_run['priority'] == 5

def test_dynamic_reload(tmp_path):
    sched = Scheduler()
    calls = []
    def cb(path):
        calls.append(path)
    config_dir = tmp_path / "cfg"
    config_dir.mkdir()
    file1 = config_dir / "one.yaml"
    file1.write_text("a: 1")
    sched.enable_dynamic_reload(str(config_dir), cb, interval=0.1)
    # modify file
    time.sleep(0.2)
    file1.write_text("a: 2")
    # create new file
    file2 = config_dir / "two.yaml"
    file2.write_text("b: 1")
    time.sleep(0.5)
    sched.stop_dynamic_reload()
    # both modification and creation should trigger
    assert any(str(file1) == p for p in calls)
    assert any(str(file2) == p for p in calls)
