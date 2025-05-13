import os
import time
import tempfile
import threading
import json
import yaml
import pytest
from datetime import datetime, date
from scheduler import Scheduler

def test_event_triggers():
    sched = Scheduler()
    results = []
    def cb(x): results.append(x)
    sched.add_event_trigger('new_fastq', cb)
    sched.fire_event('new_fastq', 42)
    assert results == [42]

def test_run_in_thread_basic():
    sched = Scheduler()
    results = []
    def work(x):
        time.sleep(0.1)
        results.append(x)
    thread = sched.run_in_thread(work, 7)
    thread.join()
    assert results == [7]

def test_concurrency_limits():
    sched = Scheduler()
    sched.set_concurrency_limits('researcher', 1)
    # first should run
    results = []
    def work():
        time.sleep(0.1)
        results.append(1)
    t1 = sched.run_in_thread(work, limit_type='researcher', concurrency_key='alice')
    # second should fail immediately
    with pytest.raises(RuntimeError):
        sched.run_in_thread(work, limit_type='researcher', concurrency_key='alice')
    t1.join()
    # after first finishes, should allow again
    t2 = sched.run_in_thread(work, limit_type='researcher', concurrency_key='alice')
    t2.join()
    assert results == [1, 1]

def test_calendar_exclusions():
    sched = Scheduler()
    sched.set_calendar_exclusions(['2023-01-01', date(2023,1,2)])
    assert sched.is_excluded(date(2023,1,1))
    assert sched.is_excluded(datetime(2023,1,2,12,0))
    assert not sched.is_excluded(date(2023,1,3))

def test_notifications():
    sched = Scheduler()
    sched.send_notification('email', 'done')
    sched.send_notification('slack', 'retry')
    assert ('email','done') in sched.notifications
    assert ('slack','retry') in sched.notifications

def test_health_checks():
    sched = Scheduler()
    assert sched.liveness()
    assert sched.readiness()
    sched.register_health_check('liveness', lambda: False)
    sched.register_health_check('readiness', lambda: False)
    assert not sched.liveness()
    assert not sched.readiness()

def test_persistence(tmp_path):
    sched = Scheduler()
    sched.persist_job('job1', {'status':'ok'})
    sched.persist_job('job2', {'status':'fail'})
    path = tmp_path / "jobs.yaml"
    sched.persist_jobs(str(path))
    # load into new scheduler
    s2 = Scheduler()
    s2.load_jobs(str(path))
    assert s2.jobs_persist == {'job1':{'status':'ok'}, 'job2':{'status':'fail'}}

def test_priority_queue_and_next_run():
    sched = Scheduler()
    # priority: lower number = higher priority
    sched.set_priority_queue(lambda data: data.get('prio',0))
    now = datetime(2023,1,1,9,0)
    later = datetime(2023,1,1,10,0)
    sched.schedule_job('a', later, {'prio':5})
    sched.schedule_job('b', now, {'prio':1})
    # next run is b at now
    assert sched.get_next_run() == now
    # add exclusion for now, next should be later
    sched.set_calendar_exclusions(['2023-01-01'])
    assert sched.get_next_run() is None

def test_dynamic_reload(tmp_path):
    sched = Scheduler()
    cfg = tmp_path / "cfg.yaml"
    yaml.safe_dump({'foo': 1}, open(cfg, 'w'))
    sched.enable_dynamic_reload(str(cfg))
    # no change yet
    assert sched.dynamic_definitions == {'foo':1}
    # modify
    time.sleep(0.01)
    yaml.safe_dump({'foo': 2}, open(cfg, 'w'))
    sched._reload_dynamic_definitions()
    assert sched.dynamic_definitions == {'foo':2}
    # test JSON
    cfgj = tmp_path / "cfg.json"
    json.dump({'bar':3}, open(cfgj, 'w'))
    sched.enable_dynamic_reload(str(cfgj))
    assert sched.dynamic_definitions == {'bar':3}
    time.sleep(0.01)
    json.dump({'bar':4}, open(cfgj, 'w'))
    sched._reload_dynamic_definitions()
    assert sched.dynamic_definitions == {'bar':4}
