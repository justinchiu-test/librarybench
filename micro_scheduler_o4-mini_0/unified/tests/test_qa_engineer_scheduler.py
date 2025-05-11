import pytest
import time
import threading
from qa_engineer.scheduler import qa_engineer.Scheduler, RedisBackend, SQLiteBackend
from datetime import datetime

@pytest.fixture
def scheduler():
    s = Scheduler()
    yield s
    s.graceful_shutdown(1)

def test_health_check(scheduler):
    assert scheduler.health_check() is True

def test_persistence_backends(scheduler):
    redis = RedisBackend()
    sqlite = SQLiteBackend()
    scheduler.set_persistence_backend(redis)
    scheduler.jobs['j'] = lambda: None
    scheduler.persistence.save_run('j', {'timestamp':'t','status':'success','attempt':1})
    assert redis.get_history('j')[0]['status']=='success'
    scheduler.set_persistence_backend(sqlite)
    scheduler.persistence.save_run('j', {'timestamp':'t2','status':'failure','attempt':2})
    hist = sqlite.get_history('j')
    assert hist[-1]['status']=='failure'

def test_trigger_job_records_success(scheduler):
    recorder = {}
    def job():
        recorder['ran'] = True
    scheduler.jobs['job1'] = job
    scheduler.set_persistence_backend(RedisBackend())
    scheduler.trigger_job('job1')
    time.sleep(0.1)
    hist = scheduler.persistence.get_history('job1')
    assert hist and hist[0]['status']=='success'
    assert recorder.get('ran') is True

def test_retry_and_backoff(scheduler):
    attempts = {'count':0}
    def flaky():
        attempts['count'] +=1
        if attempts['count'] <3:
            raise Exception("fail")
    scheduler.jobs['flaky'] = flaky
    scheduler.set_persistence_backend(RedisBackend())
    scheduler.retry_job('flaky', count=5, delay=0.01)
    scheduler.exponential_backoff('flaky', base_delay=0.01, factor=2, max_delay=0.05)
    scheduler.trigger_job('flaky')
    time.sleep(0.2)
    hist = scheduler.persistence.get_history('flaky')
    assert len(hist) == 3
    assert hist[-1]['status']=='success'

def test_schedule_delay(scheduler):
    recorder = {}
    def job():
        recorder['d'] = recorder.get('d',0)+1
    scheduler.schedule_job('delayed', job, delay=0.05)
    scheduler.set_persistence_backend(RedisBackend())
    time.sleep(0.1)
    hist = scheduler.persistence.get_history('delayed')
    assert hist and hist[0]['status']=='success'
    assert recorder['d']==1

def test_schedule_interval(scheduler):
    recorder = {'i':0}
    def job():
        recorder['i'] +=1
    scheduler.schedule_job('interval', job, interval=0.05)
    scheduler.set_persistence_backend(RedisBackend())
    time.sleep(0.18)
    hist = scheduler.persistence.get_history('interval')
    assert recorder['i'] >=3

def test_schedule_cron(scheduler):
    recorder = {'c':0}
    def job():
        recorder['c'] +=1
    scheduler.schedule_job('cron', job, cron=0.05)
    scheduler.set_persistence_backend(RedisBackend())
    time.sleep(0.18)
    hist = scheduler.persistence.get_history('cron')
    assert recorder['c'] >=3

def test_dependencies(scheduler):
    order = []
    def u():
        order.append('u')
    def i():
        order.append('i')
    scheduler.jobs['unit'] = u
    scheduler.jobs['intg'] = i
    scheduler.set_persistence_backend(RedisBackend())
    scheduler.define_dependencies({'intg':['unit']})
    scheduler.trigger_job('intg')
    time.sleep(0.05)
    scheduler.trigger_job('unit')
    time.sleep(0.05)
    # after unit success, intg should re-run
    time.sleep(0.05)
    assert 'u' in order and 'i' in order

def test_limit_resources(scheduler):
    active = {'max':0}
    lock = threading.Lock()
    def long_job():
        with lock:
            active['current'] = active.get('current',0)+1
            active['max'] = max(active['max'], active['current'])
        time.sleep(0.05)
        with lock:
            active['current'] -=1
    for j in ['a','b','c']:
        scheduler.jobs[j] = long_job
    scheduler.set_persistence_backend(RedisBackend())
    scheduler.limit_resources(2)
    for j in ['a','b','c']:
        scheduler.trigger_job(j)
    time.sleep(0.2)
    assert active['max'] == 2

def test_timezone_aware(scheduler):
    scheduler.jobs['tz'] = lambda: None
    scheduler.timezone_aware('tz','UTC')
    assert 'tz' in scheduler.timezones

def test_graceful_shutdown(scheduler):
    def long_job():
        time.sleep(0.2)
    scheduler.jobs['long'] = long_job
    scheduler.set_persistence_backend(RedisBackend())
    scheduler.trigger_job('long')
    time.sleep(0.05)
    ok = scheduler.graceful_shutdown(timeout=1)
    assert ok is True
