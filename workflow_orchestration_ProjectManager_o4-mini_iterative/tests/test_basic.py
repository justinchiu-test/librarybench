import pytest
from project_manager.task import Task, TaskState
from project_manager.runner import TaskRunner

def test_simple_success():
    runner = TaskRunner()
    def work(ctx):
        ctx.set("val", 42)
        return "done"
    t = Task("t1", work)
    runner.add_task(t)
    runner.run_all()
    assert t.state == TaskState.SUCCESS
    # output stored
    assert runner.executor  # just to use executor
    assert runner.metadata.get("t1")["state"] == "success"
    # context data
    # dynamic check via metadata
    assert runner.metadata.get("t1")["attempts"] == 1

def test_failure_no_retry():
    runner = TaskRunner()
    def fail(ctx):
        raise RuntimeError("oops")
    t = Task("t2", fail, max_retries=0)
    runner.add_task(t)
    runner.run_all()
    assert t.state == TaskState.FAILURE
    md = runner.metadata.get("t2")
    assert md["state"] == "failure"
    assert md["attempts"] == 1
