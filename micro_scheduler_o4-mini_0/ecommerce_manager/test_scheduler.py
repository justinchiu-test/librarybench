import os
import tempfile
import pytest
from datetime import datetime, timedelta, time as dt_time
import pytz
from scheduler import JobScheduler, RateLimitException

def test_manual_trigger_and_dependency():
    scheduler = JobScheduler()
    calls = []
    def job1(): calls.append('job1')
    def job2(): calls.append('job2')
    id1 = scheduler.register_recurring_job('job1', job1, interval_seconds=10)
    id2 = scheduler.schedule_job('job2', job2, run_at=datetime.utcnow())
    scheduler.add_job_dependency(id2, id1)
    # triggering job2 before job1 succeeds should fail
    with pytest.raises(RuntimeError):
        scheduler.trigger_job_manually(id2)
    # trigger job1
    assert scheduler.trigger_job_manually(id1)
    assert calls == ['job1']
    # now job2 can run
    assert scheduler.trigger_job_manually(id2)
    assert calls == ['job1', 'job2']

def test_persistence_and_load():
    scheduler = JobScheduler()
    tmp = tempfile.NamedTemporaryFile(delete=False)
    path = tmp.name
    tmp.close()
    scheduler.configure_persistence('file', path=path)
    def f(): pass
    id1 = scheduler.schedule_job('oneoff', f, run_at=datetime(2022,1,1,0,0,0))
    id2 = scheduler.register_recurring_job('rec', f, interval_seconds=30)
    scheduler.persist_jobs()
    data = scheduler.load_jobs()
    assert id1 in data and id2 in data
    assert data[id1]['name'] == 'oneoff'
    os.unlink(path)

def test_recurring_job_next_run():
    scheduler = JobScheduler()
    def f(): pass
    id1 = scheduler.register_recurring_job('rec', f, interval_seconds=1)
    job = scheduler.jobs[id1]
    first_next = job.next_run
    scheduler.trigger_job_manually(id1)
    second_next = job.next_run
    assert second_next > first_next

def test_timezone_cron_schedule():
    scheduler = JobScheduler()
    def f(): pass
    tz = 'Asia/Tokyo'
    now_utc = datetime.now(pytz.utc)
    tokyo = pytz.timezone(tz)
    local_now = now_utc.astimezone(tokyo)
    # schedule at one minute in future local time
    target = (local_now + timedelta(minutes=1))
    cron = {'hour': target.hour, 'minute': target.minute, 'second': target.second}
    id1 = scheduler.schedule_job('cronjob', f, cron=cron, timezone=tz)
    job = scheduler.jobs[id1]
    # next_run in UTC should match target local time in UTC
    expected = tokyo.localize(datetime(local_now.year, local_now.month, local_now.day, cron['hour'], cron['minute'], cron['second']))
    if expected <= local_now:
        expected = expected + timedelta(days=1)
    expected_utc = expected.astimezone(pytz.utc)
    assert abs((job.next_run - expected_utc).total_seconds()) < 1

def test_priority_sorting():
    scheduler = JobScheduler()
    def f(): pass
    id1 = scheduler.schedule_job('a', f, run_at=datetime.utcnow())
    id2 = scheduler.schedule_job('b', f, run_at=datetime.utcnow())
    scheduler.set_job_priority(id1, 5)
    scheduler.set_job_priority(id2, 1)
    result = scheduler.query_jobs()
    assert result[0]['id'] == id1
    assert result[1]['id'] == id2

def test_apply_backoff_strategy(monkeypatch):
    scheduler = JobScheduler()
    calls = []
    def flaky():
        calls.append(1)
        if len(calls) < 3:
            raise RateLimitException()
        return 'ok'
    sleeps = []
    monkeypatch.setattr(time, 'sleep', lambda x: sleeps.append(x))
    wrapped = scheduler.apply_backoff_strategy(max_retries=4, initial_delay=1, max_delay=4)(flaky)
    result = wrapped()
    assert result == 'ok'
    assert calls == [1,1,1]
    assert sleeps == [1,2]

def test_namespace_and_tags_and_query():
    scheduler = JobScheduler()
    def f(): pass
    tags = {'season':'summer','channel':'email'}
    id1 = scheduler.schedule_job('job', f, run_at=datetime.utcnow(), tags=tags, tenant='store_north')
    q = scheduler.query_jobs()
    assert q[0]['tags'] == tags
    assert q[0]['tenant'] == 'store_north'
