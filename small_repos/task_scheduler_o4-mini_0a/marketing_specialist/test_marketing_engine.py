import os
import tempfile
import datetime
import pytest
from marketing_engine import MarketingEngine

def test_track_job_stats_and_retrieve():
    engine = MarketingEngine(db_path=':memory:')
    engine.trackJobStats('camp1', 'sent', send_time=0.5)
    engine.trackJobStats('camp1', 'open', send_time=0.2)
    engine.trackJobStats('camp1', 'bounce', send_time=0.3)
    stats = engine.getJobStats('camp1')
    assert stats['send_count'] == 2  # sent + bounce
    assert stats['open_count'] == 1
    assert stats['bounce_count'] == 1
    assert pytest.approx(stats['total_send_time'], 0.0001) == 1.0
    assert stats['last_status'] == 'bounce'

def test_set_and_get_timezone():
    engine = MarketingEngine(db_path=':memory:')
    engine.setTimezone('campTZ', 'UTC')
    assert engine.getTimezone('campTZ') == 'UTC'
    with pytest.raises(ValueError):
        engine.setTimezone('campTZ', 'Invalid/Zone')

def test_schedule_and_get_next_run():
    engine = MarketingEngine(db_path=':memory:')
    dt = datetime.datetime(2025,1,1,12,0,0)
    engine.scheduleNextRun('campRun', dt)
    fetched = engine.getNextRunTime('campRun')
    assert isinstance(fetched, datetime.datetime)
    assert fetched == dt

def test_shutdown_and_pause_resume():
    engine = MarketingEngine(db_path=':memory:')
    assert not engine.isShuttingDown()
    engine.shutdownGracefully()
    assert engine.isShuttingDown()
    assert not engine.isPaused('campX')
    engine.pauseTasks('campX')
    assert engine.isPaused('campX')
    engine.resumeTasks('campX')
    assert not engine.isPaused('campX')

def test_overlap_locking():
    engine = MarketingEngine(db_path=':memory:')
    assert engine.acquireLock('c1','aud')  # no locking enabled
    engine.enableOverlapLocking()
    assert engine.acquireLock('c1','aud')
    assert not engine.acquireLock('c1','aud')
    engine.releaseLock('c1','aud')
    assert engine.acquireLock('c1','aud')

def test_tag_metadata():
    engine = MarketingEngine(db_path=':memory:')
    engine.addTagMetadata('job1', campaign='spring', channel='email')
    tags = engine.getTags('job1')
    assert tags == {'campaign':'spring','channel':'email'}
    engine.addTagMetadata('job1', campaign='summer')
    assert engine.getTags('job1')['campaign'] == 'summer'

def test_event_triggering():
    engine = MarketingEngine(db_path=':memory:')
    results = []
    def handler(p):
        results.append(p)
    engine.onEvent('signup', handler)
    engine.onEventTrigger('signup', {'user':'alice'})
    assert results == [{'user':'alice'}]

def test_retry_strategy_success_after_retries(monkeypatch):
    engine = MarketingEngine(db_path=':memory:')
    calls = {'count':0}
    @engine.retryStrategy(max_retries=2, base_delay=0, jitter=0)
    def flaky(x):
        calls['count'] += 1
        if calls['count'] < 2:
            raise ValueError("fail")
        return x*2
    assert flaky(5) == 10
    assert calls['count'] == 2

def test_retry_strategy_failure():
    engine = MarketingEngine(db_path=':memory:')
    @engine.retryStrategy(max_retries=1, base_delay=0, jitter=0)
    def always_fail():
        raise RuntimeError("oops")
    with pytest.raises(RuntimeError):
        always_fail()

def test_persistent_storage(tmp_path):
    db_file = tmp_path / "test.db"
    # First instance
    engine1 = MarketingEngine(db_path=str(db_file))
    engine1.setTimezone('p1', 'UTC')
    engine1.addTagMetadata('j1', t='v')
    engine1.trackJobStats('p1', 'sent', 1.0)
    stats1 = engine1.getJobStats('p1')
    assert stats1['send_count'] == 1
    # New instance loads same DB
    engine2 = MarketingEngine(db_path=str(db_file))
    assert engine2.getTimezone('p1') == 'UTC'
    assert engine2.getTags('j1') == {'t':'v'}
    stats2 = engine2.getJobStats('p1')
    assert stats2['send_count'] == 1
