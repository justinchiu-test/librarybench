import os
import json
import pickle
import tempfile

import pytest
from scheduler.scheduler import Scheduler
from flask import Flask

@pytest.fixture
def sched():
    return Scheduler()

def test_job_lifecycle(sched):
    # add job
    sched.jobs['j1'] = {'agent': 'us-west', 'region': 'us-west', 'status': 'running'}
    # list all
    all_jobs = sched.list_jobs()
    assert len(all_jobs) == 1
    # filter
    filtered = sched.list_jobs('us-west')
    assert len(filtered) == 1
    assert filtered[0]['agent'] == 'us-west'
    # pause
    assert sched.pause_job('j1')
    assert sched.jobs['j1']['status'] == 'paused'
    # resume
    assert sched.resume_job('j1')
    assert sched.jobs['j1']['status'] == 'running'
    # cancel
    assert sched.cancel_job('j1')
    assert sched.jobs['j1']['status'] == 'cancelled'
    # remove
    assert sched.remove_job('j1')
    assert 'j1' not in sched.jobs

def test_concurrency_and_priority(sched):
    sched.jobs['j2'] = {}
    assert sched.set_concurrency('j2', 5)
    assert sched.jobs['j2']['concurrency'] == 5
    assert sched.set_global_concurrency(10)
    assert sched.global_concurrency == 10
    assert sched.set_priority('j2', 42)
    assert sched.jobs['j2']['priority'] == 42

def test_log_and_task_context(sched):
    ctx = {'job_id': 'x', 'agent_id': 'a1', 'region': 'r1'}
    assert sched.attach_log_context(ctx)
    assert all(k in sched.logger_adapter.extra for k in ctx)
    tctx = {'trace_id': 't1', 'user': 'u1', 'commit_hash': 'c1'}
    assert sched.inject_task_context(tctx)
    assert sched.task_context['trace_id'] == 't1'

def test_run_in_sandbox(sched):
    sid = sched.run_in_sandbox('/bin/echo', {'cpu': 2, 'mem': '4GB'})
    assert sid in sched.sandboxes
    entry = sched.sandboxes[sid]
    assert entry['script'] == '/bin/echo'
    assert entry['resources']['cpu'] == 2

def test_dump_and_load_jobs(tmp_path, sched):
    # prepare jobs
    sched.jobs['a'] = {'foo': 'bar'}
    sched.jobs['b'] = {'x': 1}
    db_file = tmp_path / "test.db"
    db_url = f"sqlite:///{db_file}"
    # dump
    assert sched.dump_jobs(db_url)
    # clear and load
    sched.jobs = {}
    assert sched.load_jobs(db_url)
    assert 'a' in sched.jobs and sched.jobs['a']['foo'] == 'bar'
    assert 'b' in sched.jobs and sched.jobs['b']['x'] == 1

def test_catch_up_missed_jobs(sched):
    sched.jobs['m1'] = {'missed': True, 'status': 'new'}
    sched.jobs['m2'] = {'missed': False, 'status': 'new'}
    caught = sched.catch_up_missed_jobs()
    assert 'm1' in caught
    assert sched.jobs['m1']['status'] == 'dispatched'
    assert not sched.jobs['m1']['missed']
    assert sched.jobs['m2']['status'] == 'new'

def test_serialize_job(sched):
    payload = {'a': 1, 'b': 2}
    data_json = sched.serialize_job(payload, 'json')
    assert isinstance(data_json, str)
    assert json.loads(data_json) == payload
    data_pickle = sched.serialize_job(payload, 'pickle')
    obj = pickle.loads(data_pickle)
    assert obj == payload
    with pytest.raises(ValueError):
        sched.serialize_job(payload, 'xml')

def test_register_executor(sched):
    ex = lambda x: x*2
    assert sched.register_executor('dbl', ex)
    assert 'dbl' in sched.executors and sched.executors['dbl'] is ex

def test_api_server_endpoints(sched):
    # prepare jobs
    sched.jobs['j3'] = {'agent': 'region1', 'region': 'region1', 'status': 'running'}
    app = sched.start_api_server()
    client = app.test_client()
    # list jobs
    rv = client.get('/jobs')
    assert rv.status_code == 200
    data = rv.get_json()
    assert isinstance(data, list) and data[0]['agent'] == 'region1'
    # pause via API
    rv2 = client.post('/jobs/j3/pause')
    assert rv2.status_code == 200
    assert rv2.get_json()['ok'] is True
    assert sched.jobs['j3']['status'] == 'paused'
    # resume via API
    rv3 = client.post('/jobs/j3/resume')
    assert rv3.get_json()['ok'] is True
    assert sched.jobs['j3']['status'] == 'running'
    # set concurrency via API
    rv4 = client.post('/jobs/j3/concurrency', json={'concurrency': 3})
    assert rv4.get_json()['ok'] is True
    assert sched.jobs['j3']['concurrency'] == 3
    # set global concurrency via API
    rv5 = client.post('/concurrency', json={'global_concurrency': 7})
    assert rv5.get_json()['ok'] is True
    assert sched.global_concurrency == 7
    # set priority via API
    rv6 = client.post('/jobs/j3/priority', json={'priority': 9})
    assert rv6.get_json()['ok'] is True
    assert sched.jobs['j3']['priority'] == 9
