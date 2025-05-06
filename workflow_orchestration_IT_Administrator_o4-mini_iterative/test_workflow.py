import pytest
from it_manager.workflow import Workflow
from it_manager.tasks import Task, TaskState
from it_manager.exceptions import WorkflowFailure

def ok_task():
    return "ok"

def fail_task():
    raise RuntimeError("boom")

def test_workflow_success():
    wf = Workflow("w1")
    t1 = Task(ok_task)
    t2 = Task(ok_task)
    wf.add_task(t1)
    wf.add_task(t2)
    results = wf.run()
    assert results == ["ok", "ok"]
    assert all(t.state == TaskState.SUCCESS for t in wf.tasks)

def test_workflow_failure_propagation():
    wf = Workflow("w2")
    t1 = Task(ok_task)
    t2 = Task(fail_task, max_retries=0)
    t3 = Task(ok_task)
    wf.add_task(t1)
    wf.add_task(t2)
    wf.add_task(t3)
    with pytest.raises(WorkflowFailure):
        wf.run()
    # t3 should remain pending
    assert wf.tasks[2].state == TaskState.PENDING
