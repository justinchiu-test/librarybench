import pytest
import time
import datetime
import json
from zoneinfo import ZoneInfo
from lab_scheduler import JobScheduler

def test_add_job_and_next_run():
    js = JobScheduler()
    dt = datetime.datetime(2023, 1, 1, 12, 0, tzinfo=datetime.timezone.utc)
    job_id = js.addJob('job1', 60, dt)
    nxt = js.getNextRunTime(job_id)
    assert nxt == dt.astimezone(ZoneInfo('UTC'))

def test_set_timezone():
    js = JobScheduler()
    js.setTimezone('America/New_York')
    dt = datetime.datetime(2023, 3, 14, 15, 0, tzinfo=datetime.timezone.utc)
    job_id = js.addJob('job1', 60, dt)
    nxt = js.getNextRunTime(job_id)
    expected = dt.astimezone(ZoneInfo('America/New_York'))
    assert nxt.hour == expected.hour

def test_track_stats_and_logs():
    js = JobScheduler()
    job_id = js.addJob('job1', 60, None)
    js.trackJobStats(job_id, 'success', 1.2)
    js.trackJobStats(job_id, 'failure', 0.8)
    c = js.conn.cursor()
    c.execute('SELECT runs, success, failure, total_duration FROM stats WHERE job_id=?', (job_id,))
    runs, success, failure, total_duration = c.fetchone()
    assert runs == 2
    assert success == 1
    assert failure == 1
    assert abs(total_duration - 2.0) < 1e-6
    c.execute('SELECT COUNT(*) FROM logs WHERE job_id=?', (job_id,))
    assert c.fetchone()[0] == 2

def test_add_tag_metadata():
    js = JobScheduler()
    dt = datetime.datetime.now(datetime.timezone.utc)
    job_id = js.addJob('job1', 60, dt)
    js.addTagMetadata(job_id, {'priority': 'high', 'exp': '42'})
    c = js.conn.cursor()
    c.execute('SELECT tags FROM jobs WHERE id=?', (job_id,))
    tags = json.loads(c.fetchone()[0])
    assert tags['priority'] == 'high'
    assert tags['exp'] == '42'
    js.addTagMetadata(job_id, {'priority': 'low'})
    c.execute('SELECT tags FROM jobs WHERE id=?', (job_id,))
    tags = json.loads(c.fetchone()[0])
    assert tags['priority'] == 'low'
    assert tags['exp'] == '42'

def test_retry_strategy_success_after_retry():
    js = JobScheduler()
    calls = []
    def flaky():
        if not calls:
            calls.append(1)
            raise ValueError
        return 'ok'
    wrapped = js.retryStrategy(flaky, retries=2, backoff=0, jitter=0)
    assert wrapped() == 'ok'

def test_retry_strategy_fail():
    js = JobScheduler()
    def always_fail():
        raise RuntimeError
    wrapped = js.retryStrategy(always_fail, retries=2, backoff=0, jitter=0)
    with pytest.raises(RuntimeError):
        wrapped()

def test_overlap_locking_and_execution():
    js = JobScheduler()
    js.enableOverlapLocking('inst1')
    dt = datetime.datetime.now(datetime.timezone.utc)
    job_id = js.addJob('job1', 60, dt, instrument='inst1')
    run_order = []
    def job_func(x):
        time.sleep(0.1)
        run_order.append(x)
    t1 = js.startJob(job_id, job_func, 1)
    t2 = js.startJob(job_id, job_func, 2)
    t1.join()
    t2.join()
    assert len(run_order) == 2
    assert run_order in ([1, 2], [2, 1])

def test_pause_and_resume_and_shutdown():
    js = JobScheduler()
    dt = datetime.datetime.now(datetime.timezone.utc)
    job1 = js.addJob('job1', 60, dt, critical=False)
    job2 = js.addJob('job2', 60, dt, critical=True)
    results = []
    def fn(x):
        results.append(x)
    js.pauseTasks()
    js.startJob(job1, fn, 'a')
    t = js.startJob(job2, fn, 'b')
    t.join()
    assert results == ['b']
    js.resumeTasks()
    t2 = js.startJob(job1, fn, 'a')
    t2.join()
    assert 'a' in results
    ts = []
    def longrun():
        time.sleep(0.2)
        ts.append('done')
    job3 = js.addJob('job3', 60, dt)
    t3 = js.startJob(job3, longrun)
    js.shutdownGracefully(wait=True)
    t3.join()
    assert ts == ['done']
