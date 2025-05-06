import pytest
from Project_Manager.core.task import Task, TaskStatus
from Project_Manager.core.workflow import Workflow

def test_workflow_order_and_dependencies():
    outputs = []
    t1 = Task("A", func=lambda: outputs.append("A"), timeout=1)
    t2 = Task("B", func=lambda: outputs.append("B"), dependencies=["A"], timeout=1)
    wf = Workflow("wf1")
    wf.add_task(t1)
    wf.add_task(t2)
    status = wf.run()
    assert status == TaskStatus.SUCCESS
    assert outputs == ["A", "B"]

def test_workflow_cycle_detection():
    t1 = Task("X", func=lambda: None, dependencies=["Y"])
    t2 = Task("Y", func=lambda: None, dependencies=["X"])
    wf = Workflow("wf_cycle")
    wf.add_task(t1)
    wf.add_task(t2)
    with pytest.raises(ValueError):
        wf.run()

def test_workflow_failure_stops_dependent():
    t1 = Task("A", func=lambda: (_ for _ in ()).throw(Exception("err")), timeout=1)
    t2 = Task("B", func=lambda: "ok", dependencies=["A"], timeout=1)
    wf = Workflow("wf_fail")
    wf.add_task(t1)
    wf.add_task(t2)
    status = wf.run()
    assert status == TaskStatus.FAILED
    # Task B should be marked failed/skipped
    assert wf.tasks["B"].status == TaskStatus.FAILED

def test_workflow_versioning():
    wf = Workflow("vers", version=1)
    assert wf.version == 1
    wf.bump_version()
    assert wf.version == 2
