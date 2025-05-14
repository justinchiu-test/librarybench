import os
import tempfile
import pytest
from scheduler import Scheduler

@pytest.fixture
def sched():
    return Scheduler()

def test_schedule_and_list_jobs(sched):
    j1 = sched.schedule_job("t1", {"a": 1})
    j2 = sched.schedule_job("t2", {"b": 2})
    assert len(sched.list_jobs("t1")) == 1
    assert sched.list_jobs("t1")[0]["job_id"] == j1

def test_pause_resume_cancel(sched):
    j = sched.schedule_job("t", {})
    sched.pause_job(j)
    assert sched.jobs[j].status == "paused"
    sched.resume_job(j)
    assert sched.jobs[j].status == "scheduled"
    sched.cancel_job(j)
    assert sched.jobs[j].status == "cancelled"

def test_remove_job(sched):
    j = sched.schedule_job("t", {})
    sched.remove_job(j)
    assert j not in sched.jobs

def test_set_concurrency(sched):
    j = sched.schedule_job("t", {})
    sched.set_concurrency(j, 5)
    assert sched.jobs[j].concurrency_limit == 5
    # Semaphore should have the initialized value
    assert sched.job_semaphores[j]._value == 5

def test_set_global_concurrency(sched):
    sched.set_global_concurrency(10)
    assert sched.global_concurrency_limit == 10
    assert sched.global_semaphore._value == 10

def test_set_priority(sched):
    j = sched.schedule_job("t", {})
    sched.set_priority(j, 7)
    assert sched.jobs[j].priority == 7

def test_attach_log_context(sched):
    ctx = {"tenant": "t", "job": "j"}
    sched.attach_log_context(ctx)
    assert sched.log_adapter.extra == ctx

def test_run_in_sandbox(sched):
    code = "x = 5\ny = x + 2"
    result = sched.run_in_sandbox(code)
    assert result["x"] == 5
    assert result["y"] == 7

def test_serialize_job(sched):
    p = {"a": 1}
    s = sched.serialize_job(p, "json")
    assert s == '{"a": 1}'

def test_register_executor(sched):
    def dummy(): pass
    sched.register_executor("d", dummy)
    assert sched.executors["d"] is dummy

def test_dump_and_load_jobs(sched, tmp_path):
    j1 = sched.schedule_job("t", {"x": 1})
    j2 = sched.schedule_job("t", {"y": 2})
    f = tmp_path / "jobs.json"
    path = str(f)
    sched.dump_jobs(path)
    # clear and load
    sched.jobs = {}
    sched.load_jobs(path)
    assert j1 in sched.jobs
    assert j2 in sched.jobs
    assert sched.jobs[j1].payload == {"x": 1}

def test_catch_up_missed_jobs(sched):
    j = sched.schedule_job("t", {})
    # set next_run in past
    sched.jobs[j].next_run = sched.jobs[j].next_run.replace(year=2000)
    sched.catch_up_missed_jobs()
    assert sched.jobs[j].missed_runs == 1

def test_inject_task_context(sched):
    ctx = {"tenant": "t", "user": "u"}
    sched.inject_task_context(ctx)
    assert sched.task_context == ctx
