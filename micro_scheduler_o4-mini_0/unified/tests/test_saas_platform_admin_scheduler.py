import os
import json
import tempfile
from datetime import datetime, timedelta
import pytest
from saas_platform_admin.scheduler.scheduler import Scheduler
from dateutil import tz

def test_configure_persistence_sqlite_and_redis():
    s = Scheduler()
    p1 = s.configure_persistence('sqlite', db_path=':memory:')
    assert p1 is not None
    p2 = s.configure_persistence('redis')
    assert p2 is not None
    with pytest.raises(ValueError):
        s.configure_persistence('unknown')

def test_tenant_namespace_and_schedule_and_query():
    s = Scheduler()
    s.set_tenant_namespace('tenant1')
    run_time = datetime(2022,1,1,10,0)
    job = s.schedule_job('tenant1', 'job1', run_time, 'UTC', tags={'tier':'enterprise'})
    q = s.query_jobs('tenant1')
    assert len(q) == 1
    assert q[0]['name'] == 'job1'
    assert q[0]['tags']['tier'] == 'enterprise'

def test_add_and_enforce_dependency():
    s = Scheduler()
    s.set_tenant_namespace('t1')
    j1 = s.schedule_job('t1', 'dep', datetime.now(), 'UTC')
    j2 = s.schedule_job('t1', 'main', datetime.now(), 'UTC')
    s.add_job_dependency('t1', j2.job_id, j1.job_id)
    # Attempt before dep complete
    assert not s.trigger_job_manually('t1', j2.job_id)
    # Complete dep
    assert s.trigger_job_manually('t1', j1.job_id)
    # Now main should run
    assert s.trigger_job_manually('t1', j2.job_id)

def test_backoff_and_priority():
    s = Scheduler()
    s.set_tenant_namespace('t2')
    j = s.schedule_job('t2', 'b', datetime.now(), 'UTC', backoff_strategy=lambda n: n*5)
    # attempts start at 0
    delay1 = s.apply_backoff_strategy('t2', j.job_id)
    assert delay1 == 5
    delay2 = s.apply_backoff_strategy('t2', j.job_id)
    assert delay2 == 10
    # test default exponential
    j2 = s.schedule_job('t2', 'exp', datetime.now(), 'UTC')
    d1 = s.apply_backoff_strategy('t2', j2.job_id)
    assert d1 == 2
    s.set_job_priority('t2', j2.job_id, 10)
    q = s.query_jobs('t2')
    for item in q:
        if item['job_id'] == j2.job_id:
            assert item['priority'] == 10

def test_recurring_job_and_manual_trigger():
    s = Scheduler()
    s.set_tenant_namespace('t3')
    first = datetime(2022,1,1,0,0)
    interval = timedelta(days=1)
    j = s.register_recurring_job('t3', 'daily', first, 'UTC', interval)
    # trigger first
    assert s.trigger_job_manually('t3', j.job_id)
    # next_run updated
    q = s.query_jobs('t3')[0]
    next_run = datetime.fromisoformat(q['next_run'])
    assert next_run == first + interval

def test_persist_and_load_jobs(tmp_path):
    db_file = tmp_path / "jobs.db"
    s = Scheduler()
    s.configure_persistence('sqlite', db_path=str(db_file))
    s.set_tenant_namespace('t4')
    j = s.schedule_job('t4', 'p1', datetime(2022,1,1,12,0), 'UTC', tags={'x':1})
    s.persist_jobs()
    # create new scheduler and load
    s2 = Scheduler()
    s2.configure_persistence('sqlite', db_path=str(db_file))
    ls = s2.load_jobs('t4')
    assert len(ls) == 1
    assert ls[0].name == 'p1'
    assert ls[0].tags['x'] == 1

def test_timezone_assignment_and_dst():
    s = Scheduler()
    s.set_tenant_namespace('t5')
    # naive datetime in New York winter
    run = datetime(2022,11,5,1,30)  # DST end day
    j = s.schedule_job('t5', 'dst', run, 'America/New_York')
    # tzinfo assigned
    assert j.run_time.tzinfo is not None
    assert j.timezone == 'America/New_York'

def test_manual_trigger_nonexistent():
    s = Scheduler()
    s.set_tenant_namespace('t6')
    assert not s.trigger_job_manually('t6', 'nope')
