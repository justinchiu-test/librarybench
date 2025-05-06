import pytest
import time
from project_manager.task import Task, TaskState
from project_manager.runner import TaskRunner
from concurrent.futures import TimeoutError

def test_task_timeout():
    # real sleep will block test, override sleep_fn for runner, but timeout enforced on future
    def long_task(ctx):
        time.sleep(0.2)
        return "done"
    runner = TaskRunner()
    t = Task("slow", long_task, timeout_seconds=0.05)
    runner.add_task(t)
    runner.run_all()
    assert t.state == TaskState.FAILURE
    md = runner.metadata.get("slow")
    assert md["state"] == "failure"
    assert "TimeoutError" in md["error"]
