import pytest

from src.scheduler import Workflow, WorkflowManager, Task

def dummy():
    pass

def test_versioning_and_rollback():
    t1 = Task(name="T", func=dummy)
    wf_v1 = Workflow(name="wf", version=1, tasks={"T": t1})
    wf_v2 = Workflow(name="wf", version=2, tasks={"T": t1})
    manager = WorkflowManager()
    manager.add_workflow_version(wf_v1)
    manager.add_workflow_version(wf_v2)
    # Active version should be 2
    assert manager.list_workflows()["wf"] == 2
    # Rollback to version 1
    manager.rollback_workflow("wf", 1)
    assert manager.list_workflows()["wf"] == 1
    # Rolling back to non-existent version errors
    with pytest.raises(KeyError):
        manager.rollback_workflow("wf", 5)
    # Triggering unknown workflow errors
    with pytest.raises(KeyError):
        manager.get_active_workflow("unknown")
