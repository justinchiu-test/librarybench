import pytest
import threading
import time
import datetime
import http.client
from iot_developer.scheduler import iot_developer.Scheduler, InMemoryBackend

def test_set_persistence_backend():
    sched = Scheduler()
    class DummyBackend:
        def __init__(self):
            self.data = {}
        def set(self, k, v):
            self.data[k] = v
        def get(self, k):
            return self.data.get(k)
    dummy = DummyBackend()
    sched.set_persistence_backend(dummy)
    sched.persistence.set('key', 'value')
    assert sched.persistence.get('key') == 'value'

def test_define_dependencies_and_trigger():
    sched = Scheduler()
    order = []
    def job_a():
        order.append('A')
    def job_b():
        order.append('B')
    sched.define_dependencies('B', ['A'])
    sched.schedule_job('A', job_a)
    sched.schedule_job('B', job_b)
    sched.trigger_job('B')
    time.sleep(0.1)
    assert order == ['A', 'B']

def test_schedule_job_naive_datetime():
    sched = Scheduler()
    run_at = datetime.datetime(2023,1,1,12,0,0)
    next_run = sched.schedule_job('job1', lambda: None, run_at=run_at)
    assert next_run.tzinfo is not None
    assert next_run.hour == 12

def test_schedule_job_with_timezone():
    sched = Scheduler()
    run_at = datetime.datetime(2023,3,10,2,30,0)
    next_run = sched.schedule_job('job_tz', lambda: None, run_at=run_at, timezone='UTC')
    assert next_run.tzinfo.zone == 'UTC'
    assert next_run.hour == 2

def test_exponential_backoff():
    sched = Scheduler()
    backoff = sched.exponential_backoff(initial=1, factor=3, max_delay=10)
    assert backoff(0) == 1
    assert backoff(1) == 3
    assert backoff(2) == 9
    assert backoff(3) == 10  # capped

def test_retry_job_success_after_failures():
    sched = Scheduler()
    count = {'calls': 0}
    def flaky():
        count['calls'] += 1
        if count['calls'] < 3:
            raise ValueError("fail")
    sched.schedule_job('flaky', flaky)
    backoff = sched.exponential_backoff(initial=0.01, factor=2, max_delay=0.02)
    sched.retry_job('flaky', retries=5, backoff=backoff)
    sched.trigger_job('flaky')
    time.sleep(0.2)
    # should succeed on 3rd call
    assert count['calls'] == 3

def test_limit_resources():
    sched = Scheduler()
    sched.limit_resources(1)
    counter = {'current': 0, 'max': 0}
    lock = threading.Lock()
    def work():
        with lock:
            counter['current'] += 1
            if counter['current'] > counter['max']:
                counter['max'] = counter['current']
        time.sleep(0.1)
        with lock:
            counter['current'] -= 1
    sched.schedule_job('j1', work)
    sched.schedule_job('j2', work)
    sched.trigger_job('j1')
    sched.trigger_job('j2')
    time.sleep(0.5)
    assert counter['max'] == 1

def test_graceful_shutdown_waits():
    sched = Scheduler()
    def long_job():
        time.sleep(0.2)
    sched.schedule_job('long', long_job)
    sched.trigger_job('long')
    start = time.time()
    sched.graceful_shutdown(timeout=1)
    duration = time.time() - start
    assert duration >= 0.2

def test_health_check_and_http_server():
    sched = Scheduler()
    assert sched.health_check() is True
    server = sched.start_http_server(host='localhost', port=0)
    port = server.server_address[1]
    conn = http.client.HTTPConnection('localhost', port)
    conn.request('GET', '/health')
    resp = conn.getresponse()
    assert resp.status == 200
    data = resp.read()
    assert data == b'OK'
    sched.graceful_shutdown()
    conn.request('GET', '/health')
    resp2 = conn.getresponse()
    assert resp2.status == 503
    sched.stop_http_server()
