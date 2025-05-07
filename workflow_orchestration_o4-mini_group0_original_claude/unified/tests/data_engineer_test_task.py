import pytest
import time
from unified.workflow.task import Task, TaskState

def test_task_success():
    t = Task("t1", func=lambda x: x + 1, args=[5])
    dyn = t.run()
    assert t.state == TaskState.SUCCESS
    assert t.result == 6
    assert dyn == []

def test_task_failure_and_retries(monkeypatch):
    # fail first two times, succeed on third
    calls = {'count': 0}
    def flaky():
        calls['count'] += 1
        if calls['count'] < 3:
            raise ValueError("fail")
        return "ok"
    t = Task("t2", func=flaky, max_retries=3, retry_delay=0)
    start = time.time()
    dyn = t.run()
    duration = time.time() - start
    assert t.state == TaskState.SUCCESS
    assert t.result == "ok"
    assert calls['count'] == 3
    assert dyn == []

def test_task_exceed_retries():
    def always_fail():
        raise RuntimeError("bad")
    t = Task("t3", func=always_fail, max_retries=2, retry_delay=0)
    dyn = t.run()
    assert t.state == TaskState.FAILURE
    assert isinstance(t.exception, RuntimeError)

def test_dynamic_task_creation():
    def creator():
        from unified.workflow.task import Task
        return [Task("child", func=lambda: "c", priority=1)]
    parent = Task("parent", func=creator)
    dyn = parent.run()
    assert parent.state == TaskState.SUCCESS
    assert len(dyn) == 1
    assert dyn[0].task_id == "child"