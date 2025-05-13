import os
import threading
import tempfile
import time
import msgpack
import urllib.request
import urllib.error

import pytest
import scheduler

@pytest.fixture(autouse=True)
def clear_state():
    # Clear global state before each test
    scheduler._jobs.clear()
    scheduler._executors.clear()
    scheduler._current_log_context.clear()
    scheduler._current_task_context.clear()
    scheduler.set_global_concurrency(1)
    yield

def test_add_and_list_jobs():
    scheduler._jobs['job1'] = {'state': 'scheduled', 'concurrency': 1, 'priority': 0}
    scheduler._jobs['job2'] = {'state': 'paused', 'concurrency': 2, 'priority': 5}
    jobs = scheduler.list_jobs()
    assert set(jobs) == {'job1', 'job2'}

def test_pause_resume_cancel_remove_job():
    scheduler._jobs['j'] = {'state': 'scheduled'}
    scheduler.pause_job('j')
    assert scheduler._jobs['j']['state'] == 'paused'
    scheduler.resume_job('j')
    assert scheduler._jobs['j']['state'] == 'scheduled'
    scheduler.cancel_job('j')
    assert scheduler._jobs['j']['state'] == 'canceled'
    scheduler.remove_job('j')
    assert 'j' not in scheduler._jobs

    with pytest.raises(KeyError):
        scheduler.pause_job('nonexistent')
    with pytest.raises(KeyError):
        scheduler.remove_job('nonexistent')

def test_set_concurrency_and_priority():
    scheduler._jobs['j'] = {'state': 'scheduled', 'concurrency': 1, 'priority': 0}
    scheduler.set_concurrency('j', 5)
    assert scheduler._jobs['j']['concurrency'] == 5
    scheduler.set_priority('j', 10)
    assert scheduler._jobs['j']['priority'] == 10
    with pytest.raises(KeyError):
        scheduler.set_concurrency('x', 1)
    with pytest.raises(KeyError):
        scheduler.set_priority('x', 1)

def test_set_global_concurrency():
    scheduler.set_global_concurrency(7)
    # Internal variable not exposed but no error means success

def test_attach_and_inject_context():
    scheduler.attach_log_context({'job_id': 'j', 'model': 'm'})
    assert scheduler._current_log_context == {'job_id': 'j', 'model': 'm'}
    scheduler.inject_task_context({'request_id': 'r', 'user': 'u'})
    assert scheduler._current_task_context == {'request_id': 'r', 'user': 'u'}
    with pytest.raises(ValueError):
        scheduler.attach_log_context('not a dict')
    with pytest.raises(ValueError):
        scheduler.inject_task_context('not a dict')

def test_run_in_sandbox():
    output = scheduler.run_in_sandbox("print('hi')", {'cpu': 1, 'ram': 128})
    assert output['output'] == "Ran: print('hi')"
    assert output['limits'] == {'cpu': 1, 'ram': 128}
    with pytest.raises(ValueError):
        scheduler.run_in_sandbox("x", 'not a dict')

def test_serialize_job():
    params = {'a': 1, 'b': [1,2,3]}
    data = scheduler.serialize_job(params, 'msgpack')
    unpacked = msgpack.unpackb(data, raw=False)
    assert unpacked == params
    with pytest.raises(ValueError):
        scheduler.serialize_job(params, 'json')

def test_register_executor_and_usage():
    def dummy(x): return x*2
    scheduler.register_executor('d', dummy)
    assert 'd' in scheduler._executors
    assert scheduler._executors['d'](3) == 6

def test_dump_and_load_jobs(tmp_path):
    scheduler._jobs['j1'] = {'state': 'scheduled'}
    file_path = tmp_path / 'jobs.db'
    uri = f'file://{file_path}'
    scheduler.dump_jobs(uri)
    # mutate and reload
    scheduler._jobs.clear()
    assert scheduler._jobs == {}
    scheduler.load_jobs(uri)
    assert 'j1' in scheduler._jobs
    assert scheduler._jobs['j1']['state'] == 'scheduled'
    with pytest.raises(ValueError):
        scheduler.dump_jobs('invalid://')
    with pytest.raises(ValueError):
        scheduler.load_jobs('invalid://')

def test_catch_up_missed_jobs():
    scheduler._jobs['j1'] = {'state': 'missed'}
    scheduler._jobs['j2'] = {'state': 'scheduled'}
    scheduler.catch_up_missed_jobs()
    assert scheduler._jobs['j1']['state'] == 'scheduled'
    assert scheduler._jobs['j1']['caught_up'] is True
    assert scheduler._jobs['j2']['state'] == 'scheduled'
    assert 'caught_up' not in scheduler._jobs['j2']

def test_api_server_get_and_post():
    # setup jobs
    scheduler._jobs['j'] = {'state': 'scheduled'}
    server = scheduler.start_api_server(port=0)
    host, port = server.server_address
    time.sleep(0.1)
    # GET /jobs
    req = urllib.request.Request(f'http://{host}:{port}/jobs')
    with urllib.request.urlopen(req) as resp:
        data = resp.read()
        jobs = msgpack.unpackb(data, raw=False)
    assert 'j' in jobs
    # POST /j/pause
    req = urllib.request.Request(f'http://{host}:{port}/j/pause', method='POST')
    urllib.request.urlopen(req)
    assert scheduler._jobs['j']['state'] == 'paused'
    # POST /j/resume
    req = urllib.request.Request(f'http://{host}:{port}/j/resume', method='POST')
    urllib.request.urlopen(req)
    assert scheduler._jobs['j']['state'] == 'scheduled'
    # POST invalid
    with pytest.raises(urllib.error.HTTPError) as e:
        req = urllib.request.Request(f'http://{host}:{port}/nonexistent/pause', method='POST')
        urllib.request.urlopen(req)
    assert e.value.code == 404
    server.shutdown()
