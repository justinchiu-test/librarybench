import os
import pickle
import tempfile
import pytest
import job_scheduler

@pytest.fixture(autouse=True)
def reset_state():
    job_scheduler.jobs.clear()
    job_scheduler.missed_jobs.clear()
    job_scheduler.executors.clear()
    job_scheduler.global_current_running = 0
    job_scheduler.global_concurrency_limit = None
    job_scheduler.log_context.clear()
    job_scheduler.task_context.clear()
    job_scheduler.api_server = None

def test_run_and_list_jobs():
    job_id = job_scheduler.run_in_sandbox("echo 'hello'", {'cpu': 1, 'mem': '512MB'})
    untrusted = job_scheduler.list_jobs()
    assert any(j['id'] == job_id for j in untrusted)
    all_jobs = job_scheduler.list_jobs(filter='all')
    assert len(all_jobs) == 1

def test_pause_resume_cancel_remove():
    job_id = job_scheduler.run_in_sandbox("script", {})
    job_scheduler.pause_job(job_id)
    assert job_scheduler.jobs[job_id]['state'] == 'paused'
    job_scheduler.resume_job(job_id)
    assert job_scheduler.jobs[job_id]['state'] == 'running'
    job_scheduler.cancel_job(job_id)
    assert job_scheduler.jobs[job_id]['state'] == 'canceled'
    job_scheduler.remove_job(job_id)
    assert job_id not in job_scheduler.jobs

def test_concurrency_settings():
    job_id = job_scheduler.run_in_sandbox("script", {})
    job_scheduler.set_concurrency(job_id, 2)
    assert job_scheduler.jobs[job_id]['concurrency'] == 2
    job_scheduler.set_global_concurrency(1)
    assert job_scheduler.global_concurrency_limit == 1
    # first run is already counted, next should exceed
    with pytest.raises(RuntimeError):
        job_scheduler.run_in_sandbox("script2", {})

def test_set_priority_and_contexts():
    job_id = job_scheduler.run_in_sandbox("script", {})
    job_scheduler.set_priority(job_id, 'low')
    assert job_scheduler.jobs[job_id]['priority'] == 'low'
    log_ctx = {'job_id': job_id, 'user': 'alice'}
    job_scheduler.attach_log_context(log_ctx)
    assert job_scheduler.log_context['user'] == 'alice'
    task_ctx = {'audit_id': '1234', 'ip_address': '127.0.0.1'}
    job_scheduler.inject_task_context(task_ctx)
    assert job_scheduler.task_context['audit_id'] == '1234'

def test_serialize_job():
    args = {'foo': 'bar'}
    data = job_scheduler.serialize_job(args, 'secure_pickle')
    assert pickle.loads(data) == args
    with pytest.raises(ValueError):
        job_scheduler.serialize_job(args, 'unsafe')

def test_register_executor_and_api_server():
    def dummy_executor(task):
        return "done"
    job_scheduler.register_executor('containerd', dummy_executor)
    assert 'containerd' in job_scheduler.executors
    server = job_scheduler.start_api_server(host='127.0.0.1', port=8080)
    assert server['host'] == '127.0.0.1'
    assert server['port'] == 8080
    assert job_scheduler.api_server == server

def test_dump_and_load_jobs(tmp_path):
    job_id = job_scheduler.run_in_sandbox("echo", {'cpu': 1})
    path = tmp_path / "jobs.dat"
    job_scheduler.dump_jobs(str(path))
    # clear and load
    job_scheduler.jobs.clear()
    assert not job_scheduler.jobs
    job_scheduler.load_jobs(str(path))
    loaded = job_scheduler.list_jobs(filter='all')
    assert any(j['id'] == job_id for j in loaded)

def test_catch_up_missed_jobs():
    job = {
        'id': 'j1',
        'script': 's',
        'resources': {},
        'state': 'queued',
        'concurrency': None,
        'priority': 'normal',
        'trusted': False,
        'executor': None
    }
    job_scheduler.missed_jobs.append(job)
    job_scheduler.catch_up_missed_jobs()
    assert 'j1' in job_scheduler.jobs
    assert job_scheduler.missed_jobs == []
