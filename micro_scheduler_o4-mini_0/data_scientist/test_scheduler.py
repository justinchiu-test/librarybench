import pytest
import ast
import time
from scheduler import Scheduler, SQLiteBackend, RedisBackend, Job

def test_set_persistence_backend_sqlite(tmp_path):
    sched = Scheduler()
    db_path = str(tmp_path / "test.db")
    sched.set_persistence_backend('sqlite', {'path': db_path})
    assert isinstance(sched.persistence_backend, SQLiteBackend)
    # schedule a job and verify persistence
    def dummy(): return 1
    jid = sched.schedule_job(dummy, job_id='job1')
    data = sched.persistence_backend.load_job('job1')
    assert data is not None
    loaded = ast.literal_eval(data)
    assert loaded['id'] == 'job1'

def test_set_persistence_backend_redis():
    sched = Scheduler()
    sched.set_persistence_backend('redis', {})
    assert isinstance(sched.persistence_backend, RedisBackend)
    def dummy2(): return 2
    jid = sched.schedule_job(dummy2, job_id='job2')
    data = sched.persistence_backend.load_job('job2')
    assert isinstance(data, dict)
    assert data['id'] == 'job2'

def test_schedule_and_trigger_job():
    sched = Scheduler()
    def fn(): return 42
    jid = sched.schedule_job(fn, job_id='j3')
    res = sched.trigger_job('j3')
    assert res['status'] == 'success'
    assert res['result'] == 42
    assert res['attempts'] == 1

def test_define_dependencies():
    sched = Scheduler()
    order = []
    def a(): order.append('a'); return 'A'
    def b(): order.append('b'); return 'B'
    ja = sched.schedule_job(a, job_id='ja')
    jb = sched.schedule_job(b, job_id='jb')
    sched.define_dependencies('ja', 'jb')
    assert 'ja' in sched.jobs['jb'].dependencies
    res = sched.trigger_job('jb')
    # dependencies run first
    assert order == ['a', 'b']
    assert res['status'] == 'success'

def test_retry_job_with_backoff():
    sched = Scheduler()
    state = {'cnt': 0}
    def flaky():
        state['cnt'] += 1
        if state['cnt'] < 3:
            raise ValueError("fail")
        return "ok"
    jid = sched.schedule_job(flaky, job_id='jf')
    sched.retry_job('jf', max_retries=2, backoff_strategy='exponential')
    start = time.time()
    res = sched.trigger_job('jf')
    duration = time.time() - start
    assert res['status'] == 'success'
    assert res['attempts'] == 3
    # exponential delays: approx 1 + 2 seconds
    assert duration >= 3

def test_retry_job_exhausted():
    sched = Scheduler()
    def always_fail():
        raise RuntimeError("nope")
    jid = sched.schedule_job(always_fail, job_id='jf2')
    sched.retry_job('jf2', max_retries=1, backoff_strategy=None)
    res = sched.trigger_job('jf2')
    assert res['status'] == 'failed'
    assert res['attempts'] == 2
    assert 'nope' in res['error']

def test_exponential_backoff_decorator_success():
    sched = Scheduler()
    state = {'cnt': 0}
    @sched.exponential_backoff
    def flaky2():
        state['cnt'] += 1
        if state['cnt'] < 2:
            raise Exception("try")
        return 123
    result = flaky2()
    assert result == 123

def test_exponential_backoff_decorator_failure():
    sched = Scheduler()
    @sched.exponential_backoff
    def always():
        raise Exception("bad")
    with pytest.raises(Exception):
        always()

def test_limit_resources():
    sched = Scheduler()
    sched.limit_resources(cpu=3, gpu=1)
    assert sched.resource_limits['cpu'] == 3
    assert sched.resource_limits['gpu'] == 1

def test_health_check():
    sched = Scheduler()
    def x(): return 0
    jid1 = sched.schedule_job(x, job_id='h1')
    jid2 = sched.schedule_job(x, job_id='h2')
    hc = sched.health_check()
    assert hc['status'] == 'running'
    assert set(hc['jobs']) == {'h1', 'h2'}

def test_graceful_shutdown():
    sched = Scheduler()
    assert not sched.shutting_down
    sched.graceful_shutdown()
    assert sched.shutting_down

def test_timezone_aware():
    sched = Scheduler()
    def tzfn(): return "tz"
    jid = sched.schedule_job(tzfn, job_id='tz1', timezone='UTC+2')
    job = sched.jobs['tz1']
    assert job.timezone == 'UTC+2'
