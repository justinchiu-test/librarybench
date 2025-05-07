import pytest
from unified.workflow.manager import WorkflowManager
from unified.workflow.task import Task

def test_add_and_run_tasks():
    mgr = WorkflowManager()
    results = []
    def make_task(i):
        return Task(f"t{i}", func=lambda i=i: results.append(i), priority=i)
    for i in [3, 1, 2]:
        mgr.add_task(make_task(i))
    mgr.run_all()
    # since priority 1 runs first, then 2, then 3
    assert results == [1, 2, 3]

def test_duplicate_task_id():
    mgr = WorkflowManager()
    t1 = Task("dup", func=lambda: None)
    mgr.add_task(t1)
    with pytest.raises(ValueError):
        mgr.add_task(Task("dup", func=lambda: None))

def test_get_states():
    mgr = WorkflowManager()
    t = Task("a", func=lambda: None)
    mgr.add_task(t)
    mgr.run_all()
    states = mgr.get_all_states()
    assert states == {"a": "success"}