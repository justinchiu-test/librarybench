import os
import json
import asyncio
import time
import logging
import pytest
from scheduler import MicroScheduler

@pytest.fixture
def scheduler():
    return MicroScheduler()

def test_schedule_and_list_jobs(scheduler):
    def dummy_job():
        pass
    scheduler.schedule_recurring_job('job1', dummy_job, 5, tags=['news'])
    jobs = scheduler.list_jobs()
    assert len(jobs) == 1
    job = jobs[0]
    assert job['name'] == 'job1'
    assert job['tags'] == ['news']
    assert job['last_status'] is None
    assert job['run_count'] == 0
    assert job['next_run'] > time.time()

def test_adjust_interval(scheduler):
    def dummy():
        pass
    scheduler.schedule_recurring_job('job2', dummy, 10)
    old_next_run = scheduler.jobs['job2']['next_run']
    scheduler.adjust_interval('job2', 20)
    assert scheduler.jobs['job2']['interval'] == 20
    assert scheduler.jobs['job2']['next_run'] > old_next_run

def test_persist_jobs_json(tmp_path, scheduler):
    def dummy():
        pass
    scheduler.schedule_recurring_job('job3', dummy, 15, tags=['test'])
    file_path = tmp_path / "jobs.json"
    scheduler.persist_jobs(str(file_path))
    with open(file_path) as f:
        data = json.load(f)
    assert 'job3' in data
    info = data['job3']
    assert info['interval'] == 15
    assert info['tags'] == ['test']
    assert 'next_run' in info
    assert info['last_status'] is None
    assert info['run_count'] == 0

def test_persist_jobs_pickle(tmp_path, scheduler):
    def dummy():
        pass
    scheduler.schedule_recurring_job('job4', dummy, 25)
    file_path = tmp_path / "jobs.pkl"
    scheduler.persist_jobs(str(file_path))
    import pickle
    with open(file_path, 'rb') as f:
        data = pickle.load(f)
    assert 'job4' in data
    info = data['job4']
    assert info['interval'] == 25

def test_register_and_use_hook(scheduler):
    result = {}
    def hook(dom):
        result['called'] = True
    scheduler.register_hook('test_hook', hook)
    assert 'test_hook' in scheduler.hooks
    scheduler.hooks['test_hook']('domain')
    assert result.get('called', False)

def test_expose_metrics(scheduler):
    metrics = scheduler.expose_metrics()
    assert 'histogram' in metrics
    assert 'success_counter' in metrics
    assert 'failure_counter' in metrics
    assert 'queue_gauge' in metrics

def test_attach_logger(scheduler):
    logger = logging.getLogger('test')
    scheduler.attach_logger(logger)
    assert scheduler.logger is logger

class DummyResponse:
    def __init__(self, status, text):
        self.status = status
        self._text = text
    async def text(self):
        return self._text
    async def __aenter__(self):
        return self
    async def __aexit__(self, exc_type, exc, tb):
        pass

class DummySession:
    def __init__(self, responses):
        self.responses = responses
    async def get(self, url):
        return self.responses[url]
    async def __aenter__(self):
        return self
    async def __aexit__(self, exc_type, exc, tb):
        pass

@pytest.mark.asyncio
async def test_run_async_job(monkeypatch, scheduler):
    urls = ['http://a', 'http://b']
    responses = {
        'http://a': DummyResponse(200, 'OK'),
        'http://b': DummyResponse(404, 'Not Found'),
    }
    async def dummy_session(*args, **kwargs):
        return DummySession(responses)
    monkeypatch.setattr('scheduler.scheduler.aiohttp.ClientSession', dummy_session)
    results = await scheduler.run_async_job(urls)
    statuses = {r['url']: r.get('status') for r in results}
    assert statuses['http://a'] == 200
    assert statuses['http://b'] == 404

def test_graceful_shutdown(scheduler):
    scheduler._inflight_tasks.add(object())
    scheduler.graceful_shutdown(timeout=0.01)
    assert scheduler.shutdown_flag
    assert len(scheduler._inflight_tasks) == 0

def test_coordinate_leader_election(monkeypatch, scheduler):
    class DummyLock:
        def __init__(self, name, timeout):
            pass
        def acquire(self, blocking=False):
            return True
    class DummyRedisClient:
        def lock(self, name, timeout):
            return DummyLock(name, timeout)
    monkeypatch.setattr('scheduler.scheduler.redis.Redis', lambda *args, **kwargs: DummyRedisClient())
    acquired = asyncio.get_event_loop().run_until_complete(scheduler.coordinate_leader_election('lock', 5))
    assert acquired
