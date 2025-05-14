import pytest
import threading
import datetime
import os
import json
import time
from campaign_scheduler import CampaignScheduler

def test_add_and_trigger_event():
    sched = CampaignScheduler()
    results = []
    def cb(x):
        results.append(x)
    sched.add_event_trigger('signup', cb)
    sched.trigger_event('signup', 42)
    assert results == [42]

def test_run_in_thread_decorator():
    sched = CampaignScheduler()
    @sched.run_in_thread
    def f(x, results):
        results.append(x)
    results = []
    t = f(10, results)
    t.join(timeout=1)
    assert results == [10]

def test_calendar_exclusions():
    sched = CampaignScheduler()
    today = datetime.date.today()
    saturday = today + datetime.timedelta((5 - today.weekday()) % 7)
    dt = datetime.datetime.combine(saturday, datetime.time())
    sched.set_calendar_exclusions(weekends=True)
    # schedule on weekend should be excluded
    sched.schedule_job('camp1', dt, lambda: None)
    assert len(sched.jobs_heap) == 0
    assert any('excluded' in n['message'] for n in sched.notifications)

def test_concurrency_limits():
    sched = CampaignScheduler()
    sched.set_concurrency_limits('campA', 2)
    now = datetime.datetime.utcnow()
    f = lambda: None
    sched.schedule_job('campA', now, f)
    sched.schedule_job('campA', now, f)
    # third should be blocked
    sched.schedule_job('campA', now, f)
    assert len([n for n in sched.notifications if 'limit' in n['message']]) == 1
    assert len(sched.jobs_heap) == 2

def test_priority_queue_and_next_run():
    sched = CampaignScheduler()
    now = datetime.datetime.utcnow()
    earlier = now + datetime.timedelta(seconds=10)
    later = now + datetime.timedelta(seconds=20)
    f = lambda: None
    sched.schedule_job('camp1', later, f, priority=5)
    sched.schedule_job('camp1', earlier, f, priority=1)
    nr = sched.get_next_run('camp1')
    # next run should be the earlier one
    assert abs((nr - earlier).total_seconds()) < 0.1

def test_persist_and_load_jobs(tmp_path):
    sched = CampaignScheduler()
    now = datetime.datetime.utcnow()
    f = lambda: None
    sched.schedule_job('campX', now, f, priority=3)
    file_path = tmp_path / "jobs.json"
    sched.persist_jobs(to='json', path=str(file_path))
    # create new scheduler and load
    sched2 = CampaignScheduler()
    sched2.load_jobs(source='json', path=str(file_path))
    nr = sched2.get_next_run('campX')
    assert abs((nr - now).total_seconds()) < 0.1

def test_health_check():
    sched = CampaignScheduler()
    health = sched.register_health_check()
    assert health() is True
    sched.health_up = False
    assert health() is False

def test_dynamic_reload(tmp_path):
    # create config file
    config = {'jobs': [
        {'campaign_name': 'dyn', 'run_time_ts': time.time() + 5, 'priority': 2}
    ]}
    file_path = tmp_path / "config.json"
    with open(file_path, 'w') as f:
        json.dump(config, f)
    sched = CampaignScheduler()
    sched.enable_dynamic_reload(str(file_path), interval=0.1)
    # wait for watcher to pick up
    time.sleep(0.2)
    # jobs should be loaded
    assert any(job[2] == 'dyn' for job in sched.jobs_heap)
    # modify file
    config2 = {'jobs': [
        {'campaign_name': 'dyn2', 'run_time_ts': time.time() + 10, 'priority': 1}
    ]}
    with open(file_path, 'w') as f:
        json.dump(config2, f)
    time.sleep(0.2)
    # old job removed, new job present
    assert any(job[2] == 'dyn2' for job in sched.jobs_heap)
