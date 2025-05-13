import os
import sqlite3
import yaml
import time
import datetime
import pytest
from pipeline_manager import PipelineManager

def test_persistent_storage(tmp_path):
    defs = {'jobs': [{'id': 'job1', 'schedule': '*/5 * * * *'}]}
    yaml_file = tmp_path / "defs.yaml"
    mgr = PipelineManager(db_path=str(tmp_path/"test.db"), yaml_path=str(yaml_file))
    mgr.persistentStorage(defs)
    with open(yaml_file) as f:
        data = yaml.safe_load(f)
    assert data == defs

def test_set_timezone():
    mgr = PipelineManager(db_path=":memory:")
    mgr.setTimezone('UTC')
    assert mgr.timezone.zone == 'UTC'
    mgr.setTimezone('Europe/Berlin')
    assert 'Berlin' in mgr.timezone.zone

def test_add_tag_metadata():
    mgr = PipelineManager(db_path=":memory:")
    mgr.addTagMetadata('job1', {'dataset': 'mnist', 'model': 'resnet'})
    c = mgr.conn.cursor()
    rows = c.execute('SELECT key, value FROM tags WHERE job_id=?', ('job1',)).fetchall()
    assert set(rows) == {('dataset', 'mnist'), ('model', 'resnet')}

def test_track_job_stats():
    mgr = PipelineManager(db_path=":memory:")
    mgr.trackJobStats('job1', True, 2.0, '')
    mgr.trackJobStats('job1', False, 4.0, 'error')
    c = mgr.conn.cursor()
    stats = c.execute('SELECT total_runs, success_count, failure_count, avg_duration FROM job_stats WHERE job_id=?', ('job1',)).fetchone()
    assert stats[0] == 2
    assert stats[1] == 1
    assert stats[2] == 1
    assert pytest.approx(stats[3], rel=1e-2) == 3.0

def test_schedule_and_get_next_run_time():
    mgr = PipelineManager(db_path=":memory:")
    mgr.setTimezone('UTC')
    # Schedule a job every 60 seconds
    mgr.scheduleJob('job1', lambda: None, interval_seconds=60)
    nxt = mgr.getNextRunTime('job1')
    assert isinstance(nxt, datetime.datetime)
    delta = (nxt - datetime.datetime.now(datetime.timezone.utc)).total_seconds()
    assert 0 < delta <= 60

def test_pause_and_resume_tasks():
    mgr = PipelineManager(db_path=":memory:")
    mgr.setTimezone('UTC')
    mgr.scheduleJob('job2', lambda: None, interval_seconds=60)
    # Pause
    mgr.pauseTasks('job2')
    job = mgr.scheduler.get_job(mgr.job_map['job2'])
    assert job.next_run_time is None
    # Resume
    mgr.resumeTasks('job2')
    job = mgr.scheduler.get_job(mgr.job_map['job2'])
    assert job.next_run_time is not None

def test_enable_overlap_locking():
    mgr = PipelineManager(db_path=":memory:")
    mgr.enableOverlapLocking('jobX')
    c = mgr.conn.cursor()
    lock = c.execute('SELECT locked FROM locks WHERE job_id=?', ('jobX',)).fetchone()
    assert lock == (0,)

def test_retry_strategy():
    mgr = PipelineManager(db_path=":memory:")
    calls = {'count': 0}
    def flaky(x):
        calls['count'] += 1
        if calls['count'] < 3:
            raise ValueError("fail")
        return x * 2
    wrapped = mgr.retryStrategy(flaky, max_retries=5, initial_backoff=0.01)
    result = wrapped(5)
    assert result == 10
    assert calls['count'] == 3

def test_on_event_trigger_and_simulation():
    mgr = PipelineManager(db_path=":memory:")
    file_events = []
    stream_events = []
    def file_cb(fname):
        file_events.append(fname)
    def stream_cb(msg):
        stream_events.append(msg)
    mgr.onEventTrigger(file_cb, 'file', directory='/tmp')
    mgr.onEventTrigger(stream_cb, 'stream', stream='kafka-topic')
    mgr.simulateFileEvent('/tmp', 'data.csv')
    mgr.simulateStreamEvent('kafka-topic', {'key': 'value'})
    assert file_events == ['data.csv']
    assert stream_events == [{'key': 'value'}]

def test_shutdown_gracefully():
    mgr = PipelineManager(db_path=":memory:")
    mgr.shutdownGracefully()
    assert mgr.shutdown_flag.is_set()
    # Further scheduling should fail
    with pytest.raises(Exception):
        mgr.scheduleJob('jobZ', lambda: None, interval_seconds=10)
