import pytest
import time
import os
from datetime import datetime, timedelta
from iot_scheduler import IoTScheduler

def test_event_trigger():
    scheduler = IoTScheduler()
    called = []
    def cb(x):
        called.append(x)
        return x * 2
    scheduler.add_event_trigger('test', cb)
    result = scheduler.fire_event('test', 5)
    assert result == 10
    assert called == [5]
    with pytest.raises(KeyError):
        scheduler.fire_event('unknown')

def test_run_in_thread():
    scheduler = IoTScheduler()
    result = []
    def work(x):
        time.sleep(0.1)
        result.append(x)
    t = scheduler.run_in_thread(work, 42)
    t.join(timeout=1)
    assert result == [42]

def test_calendar_exclusions():
    scheduler = IoTScheduler()
    now = datetime.now()
    later = now + timedelta(hours=1)
    scheduler.set_calendar_exclusions([(now, later)])
    assert scheduler.is_excluded(now + timedelta(minutes=30))
    assert not scheduler.is_excluded(now - timedelta(hours=1))

def test_send_notification():
    scheduler = IoTScheduler()
    scheduler.send_notification('email', 'Test message')
    scheduler.send_notification('sms', 'Another message')
    notes = scheduler.get_notifications()
    assert ('email', 'Test message') in notes
    assert ('sms', 'Another message') in notes

def test_concurrency_limits():
    scheduler = IoTScheduler()
    scheduler.set_concurrency_limits('job', 1)
    assert scheduler.acquire_slot('job', timeout=0.1) is True
    assert scheduler.acquire_slot('job', timeout=0.1) is False
    scheduler.release_slot('job')
    assert scheduler.acquire_slot('job', timeout=0.1) is True

def test_health_check():
    scheduler = IoTScheduler()
    scheduler.register_health_check('/health')
    status = scheduler.get_health()
    assert status['status'] == 'ok'
    assert '/health' in status['endpoints']

def test_persist_jobs(tmp_path):
    db_file = tmp_path / "jobs.db"
    scheduler = IoTScheduler()
    scheduler.persist_jobs(storage='sqlite', db_path=str(db_file))
    scheduler.add_job('job1', 'data1')
    scheduler.add_job('job2', 'data2')
    jobs = scheduler.get_jobs()
    assert ('job1', 'data1') in jobs
    assert ('job2', 'data2') in jobs

def test_priority_queue():
    scheduler = IoTScheduler()
    tasks = [(2, 'low'), (1, 'high'), (3, 'lower')]
    scheduler.set_priority_queue(tasks)
    assert scheduler.get_next_task() == 'high'
    assert scheduler.get_next_task() == 'low'
    assert scheduler.get_next_task() == 'lower'
    assert scheduler.get_next_task() is None

def test_schedule_and_next_run():
    scheduler = IoTScheduler()
    now = datetime.now()
    run1 = now + timedelta(minutes=10)
    run2 = now + timedelta(minutes=5)
    scheduler.schedule_job(run1, 'job1')
    scheduler.schedule_job(run2, 'job2')
    next_run = scheduler.get_next_run()
    assert next_run == run2

def test_dynamic_reload(tmp_path):
    file = tmp_path / "config.txt"
    file.write_text("version1")
    scheduler = IoTScheduler()
    scheduler.enable_dynamic_reload(str(file))
    assert scheduler.config_data == "version1"
    time.sleep(0.1)
    file.write_text("version2")
    reloaded = scheduler.check_reload()
    assert reloaded is True
    assert scheduler.config_data == "version2"
