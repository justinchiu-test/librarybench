import os
import time
import datetime
import tempfile
import pickle
import pytest
from iot_coordinator.scheduler import iot_coordinator.Scheduler, FilePersistence, RedisPersistence, Job

class FakeRedis:
    def __init__(self):
        self.store = {}
    def set(self, key, value):
        self.store[key] = value
    def get(self, key):
        return self.store.get(key, None)

def test_set_and_query_tenant_namespace():
    sched = Scheduler()
    sched.set_tenant_namespace('fleet_north')
    sched.schedule_job('job1', 'UTC', {'type':'daily','hour':1,'minute':0})
    jobs = sched.query_jobs()
    assert len(jobs) == 1
    assert jobs[0].tenant == 'fleet_north'
    assert jobs[0].name == 'job1'

def test_add_job_dependency():
    sched = Scheduler()
    sched.set_tenant_namespace('fleet')
    sched.schedule_job('A', 'UTC', {'type':'daily','hour':0,'minute':0})
    sched.schedule_job('B', 'UTC', {'type':'daily','hour':1,'minute':0})
    sched.add_job_dependency('B', 'A')
    jobs = sched.query_jobs()
    jb = next(j for j in jobs if j.name=='B')
    assert 'A' in jb.dependencies

def test_trigger_job_manually_and_recurring():
    sched = Scheduler()
    sched.set_tenant_namespace('fleetX')
    job = sched.register_recurring_job('diag', 'UTC', {'type':'daily','hour':0,'minute':0})
    before = job.next_run
    sched.trigger_job_manually('diag')
    assert job.status == 'manual'
    assert job.last_run is not None
    assert job.next_run != before

def test_backoff_strategy_and_failure():
    sched = Scheduler()
    sched.set_tenant_namespace('fleet')
    sched.schedule_job('edge', 'UTC', {'type':'daily','hour':0,'minute':0})
    sched.apply_backoff_strategy('edge', base=1, factor=2, max_backoff=5)
    sched.record_failure('edge')
    first = sched._get_job('edge').next_run
    sched.record_failure('edge')
    second = sched._get_job('edge').next_run
    delta1 = (first - datetime.datetime.now(datetime.timezone.utc)).total_seconds()
    delta2 = (second - first).total_seconds()
    assert pytest.approx(delta1, rel=0.5) in [1,2,3,4,5]
    assert delta2 >= delta1

def test_priority_ordering():
    sched = Scheduler()
    sched.set_tenant_namespace('fleet')
    sched.schedule_job('low', 'UTC', {'type':'daily','hour':0,'minute':0})
    sched.schedule_job('high', 'UTC', {'type':'daily','hour':0,'minute':0})
    sched.set_job_priority('high', 10)
    jobs = sched.query_jobs()
    assert jobs[0].name == 'high'
    assert jobs[1].name == 'low'

def test_tags_query():
    sched = Scheduler()
    sched.set_tenant_namespace('f1')
    sched.schedule_job('j1', 'UTC', {'type':'daily','hour':0,'minute':0}, tags={'region':'eu-west-1'})
    res = sched.query_jobs(tags={'region':'eu-west-1'})
    assert len(res) == 1
    assert res[0].name == 'j1'

def test_file_persistence(tmp_path):
    sched = Scheduler()
    sched.set_tenant_namespace('tenant')
    sched.schedule_job('persist', 'UTC', {'type':'daily','hour':0,'minute':0})
    fp = tmp_path / "jobs.pkl"
    sched.configure_persistence('file', filepath=str(fp))
    sched.persist_jobs()
    # load into new scheduler
    sched2 = Scheduler()
    sched2.configure_persistence('file', filepath=str(fp))
    sched2.load_jobs()
    sched2.set_tenant_namespace('tenant')
    jobs = sched2.query_jobs()
    assert len(jobs) == 1
    assert jobs[0].name == 'persist'

def test_redis_persistence():
    fake = FakeRedis()
    sched = Scheduler()
    sched.set_tenant_namespace('t1')
    sched.schedule_job('rjob', 'UTC', {'type':'daily','hour':0,'minute':0})
    sched.configure_persistence('redis', client=fake, key='k1')
    sched.persist_jobs()
    sched2 = Scheduler()
    sched2.configure_persistence('redis', client=fake, key='k1')
    sched2.load_jobs()
    sched2.set_tenant_namespace('t1')
    jobs = sched2.query_jobs()
    assert len(jobs) == 1
    assert jobs[0].name == 'rjob'

def test_timezone_next_run_correct_timezone():
    sched = Scheduler()
    sched.set_tenant_namespace('tz')
    job = sched.schedule_job('tzjob', 'Australia/Sydney', {'type':'daily','hour':10,'minute':30})
    # next_run should be UTC datetime corresponding to 10:30 Sydney
    nr = job.next_run
    assert nr.tzinfo == datetime.timezone.utc
    # Convert back to Sydney and check hour/minute
    from zoneinfo import ZoneInfo
    local = nr.astimezone(ZoneInfo('Australia/Sydney'))
    assert local.hour == 10 and local.minute == 30

def test_register_recurring_job_flag():
    sched = Scheduler()
    sched.set_tenant_namespace('fleet')
    job = sched.register_recurring_job('rec', 'UTC', {'type':'daily','hour':5,'minute':0})
    assert job.recurring is True
    jobs = sched.query_jobs()
    assert any(j.name=='rec' and j.recurring for j in jobs)
