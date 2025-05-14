import os
import json
import time
import tempfile
import pytest
from datetime import datetime, timedelta
from smarthome.scheduler import SmartHomeScheduler

def test_schedule_and_get_next_run():
    scheduler = SmartHomeScheduler(storage_file=':memory:')
    dt = datetime(2023, 1, 1, 7, 0, 0)
    scheduler.scheduleJob('job1', dt, lambda: None)
    assert scheduler.getNextRunTime('job1') == dt

def test_add_tag_metadata():
    scheduler = SmartHomeScheduler(storage_file=':memory:')
    dt = datetime.now()
    scheduler.scheduleJob('job2', dt, lambda: None)
    scheduler.addTagMetadata('job2', {'security', 'lighting'})
    job = scheduler.jobs['job2']
    assert 'security' in job['tags'] and 'lighting' in job['tags']

def test_shutdown_prevents_run():
    flag = {'count': 0}
    def cb():
        flag['count'] += 1
    scheduler = SmartHomeScheduler(storage_file=':memory:')
    dt = datetime.now()
    scheduler.scheduleJob('job3', dt, cb)
    scheduler.shutdownGracefully()
    scheduler.runJob('job3')
    assert flag['count'] == 0

def test_pause_and_resume():
    flag = {'count': 0}
    def cb():
        flag['count'] += 1
    scheduler = SmartHomeScheduler(storage_file=':memory:')
    dt = datetime.now()
    scheduler.scheduleJob('job4', dt, cb)
    scheduler.pauseTasks(['job4'])
    scheduler.runJob('job4')
    assert flag['count'] == 0
    scheduler.resumeTasks(['job4'])
    scheduler.runJob('job4')
    assert flag['count'] == 1

def test_overlap_locking():
    runs = {'count': 0}
    def cb():
        runs['count'] += 1
        # simulate long running
        time.sleep(0.01)
    scheduler = SmartHomeScheduler(storage_file=':memory:')
    dt = datetime.now()
    scheduler.scheduleJob('job5', dt, cb)
    scheduler.enableOverlapLocking('job5')
    # Manually set running to simulate overlap
    scheduler.jobs['job5']['running'] = True
    scheduler.runJob('job5')
    assert runs['count'] == 0
    # clear running
    scheduler.jobs['job5']['running'] = False
    scheduler.runJob('job5')
    assert runs['count'] == 1

def test_persistent_storage(tmp_path):
    file = tmp_path / "storage.json"
    scheduler = SmartHomeScheduler(storage_file=str(file))
    dt = datetime.now()
    scheduler.scheduleJob('job6', dt, lambda: None)
    scheduler.addTagMetadata('job6', {'tag1'})
    scheduler.pauseTasks(['job6'])
    # reload
    scheduler2 = SmartHomeScheduler(storage_file=str(file))
    assert 'job6' in scheduler2.jobs
    job = scheduler2.jobs['job6']
    assert job['paused'] is True
    assert 'tag1' in job['tags']

def test_retry_strategy_success_after_retries():
    calls = {'count': 0}
    def flaky(x):
        calls['count'] += 1
        if calls['count'] < 3:
            raise ValueError("fail")
        return x * 2
    delays = []
    def fake_sleep(d):
        delays.append(d)
    scheduler = SmartHomeScheduler(storage_file=':memory:')
    result = scheduler.retryStrategy(flaky, 5, retries=4, base_delay=0.1, jitter=0.0, sleep_func=fake_sleep)
    assert result == 10
    assert calls['count'] == 3
    assert len(delays) == 2
    assert pytest.approx(delays[0], rel=0.1) == 0.1
    assert pytest.approx(delays[1], rel=0.1) == 0.2

def test_on_event_trigger_and_shutdown():
    flag = {'count': 0}
    def cb(a, b):
        flag['count'] += a + b
    scheduler = SmartHomeScheduler(storage_file=':memory:')
    scheduler.onEventTrigger('motion', cb)
    scheduler.triggerEvent('motion', 1, 2)
    assert flag['count'] == 3
    scheduler.shutdownGracefully()
    scheduler.triggerEvent('motion', 1, 2)
    assert flag['count'] == 3

def test_set_timezone_affects_next_time():
    scheduler = SmartHomeScheduler(storage_file=':memory:')
    scheduler.setTimezone('UTC')
    dt = datetime(2023, 1, 1, 7, 0, 0)
    scheduler.scheduleJob('job7', dt, lambda: None)
    next_dt = scheduler.getNextRunTime('job7')
    assert next_dt.tzinfo is not None
    assert next_dt.hour == 7
