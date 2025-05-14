import threading
import time
import pytest
import datetime
import zoneinfo
import scheduler

def setup_function():
    # Reset global state before each test
    scheduler.shutdown_event.clear()
    scheduler._partial_data.clear()
    scheduler.jobs.clear()
    scheduler.schedules.clear()
    scheduler.dependencies.clear()
    scheduler.set_persistence_backend('sqlite')

def test_graceful_shutdown_persists_partial_data():
    assert scheduler.graceful_shutdown(abort_threshold=0.1) is True
    data = scheduler.get_partial_data()
    assert isinstance(data, list)
    assert len(data) == 1
    assert 'timestamp' in data[0]

def test_health_check_ok():
    status = scheduler.health_check()
    assert isinstance(status, dict)
    assert status.get('status') == 'ok'

def test_trigger_job_success_and_failure():
    # Register a job
    scheduler.jobs['test_job'] = lambda x, y: x + y
    result = scheduler.trigger_job('test_job', 2, 3)
    assert result == 5
    with pytest.raises(ValueError):
        scheduler.trigger_job('nonexistent')

def test_schedule_job_records_schedule():
    ok = scheduler.schedule_job('j1', cron='0 0 * * *', delay=10, timezone='UTC')
    assert ok is True
    assert 'j1' in scheduler.schedules
    cfg = scheduler.schedules['j1']
    assert cfg['cron'] == '0 0 * * *'
    assert cfg['delay'] == 10
    assert cfg['timezone'] == 'UTC'

def test_set_and_get_persistence_backend():
    scheduler.set_persistence_backend('redis')
    assert scheduler.get_persistence_backend() == 'redis'
    scheduler.set_persistence_backend('sqlite')
    assert scheduler.get_persistence_backend() == 'sqlite'
    with pytest.raises(ValueError):
        scheduler.set_persistence_backend('unknown')

def test_timezone_aware_decorator_attaches_timezone():
    @scheduler.timezone_aware('Europe/Berlin')
    def job():
        return True
    assert hasattr(job, '_timezone')
    tz = job._timezone
    assert isinstance(tz, zoneinfo.ZoneInfo)
    assert tz.key == 'Europe/Berlin'
    assert job() is True

def test_exponential_backoff_success_after_retries():
    calls = {'count': 0}
    @scheduler.exponential_backoff(initial=0.01, multiplier=1, max_time=1)
    def flaky():
        calls['count'] += 1
        if calls['count'] < 3:
            raise Exception("fail")
        return "success"
    result = flaky()
    assert result == "success"
    assert calls['count'] == 3

def test_exponential_backoff_fails_after_max_time():
    @scheduler.exponential_backoff(initial=0.1, multiplier=2, max_time=0.05)
    def always_fail():
        raise Exception("always")
    with pytest.raises(Exception):
        always_fail()

def test_define_dependencies_and_trigger():
    def step1():
        return 1
    def step2(x):
        return x + 2
    runner = scheduler.define_dependencies('chain', [step1, step2])
    # runner is registered
    assert 'chain' in scheduler.jobs
    result = scheduler.trigger_job('chain')
    assert result == 3
    # Direct call of runner
    assert runner() == 3

def test_retry_job_decorator():
    calls = {'count': 0}
    @scheduler.retry_job(max_attempts=4, multiplier=0)
    def flaky():
        calls['count'] += 1
        if calls['count'] < 3:
            raise ValueError("retry")
        return "done"
    result = flaky()
    assert result == "done"
    assert calls['count'] == 3
    # Exceed max attempts
    calls['count'] = 0
    @scheduler.retry_job(max_attempts=2, multiplier=0)
    def always_fail():
        calls['count'] += 1
        raise RuntimeError("err")
    with pytest.raises(RuntimeError):
        always_fail()
    assert calls['count'] == 2

def test_limit_resources_decorator_serialization():
    order = []
    @scheduler.limit_resources(max_concurrent=1)
    def task(name, delay):
        order.append(name)
        time.sleep(delay)
        order.append(name + "_done")
    # Run two tasks in threads
    t1 = threading.Thread(target=task, args=('a', 0.1))
    t2 = threading.Thread(target=task, args=('b', 0.1))
    t1.start()
    time.sleep(0.05)  # ensure overlap attempt
    t2.start()
    t1.join()
    t2.join()
    # Since max_concurrent=1, 'a_done' must appear before 'b' starts
    assert order[0] == 'a'
    assert order[1] == 'a_done'
    assert order[2] == 'b'
    assert order[3] == 'b_done'
