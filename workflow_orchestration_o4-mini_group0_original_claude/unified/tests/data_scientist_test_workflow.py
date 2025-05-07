import pytest
from unified.task_manager import WorkflowManager, Task

def test_workflow_execution_order():
    manager = WorkflowManager()
    wf_id = manager.register_workflow("wf1")
    order = []

    def a():
        order.append("a")
    def b():
        order.append("b")
    def c():
        order.append("c")

    t1 = Task("a", a)
    t2 = Task("b", b, dependencies=["a"])
    t3 = Task("c", c, dependencies=["b"])

    manager.add_task_to_workflow(wf_id, t1)
    manager.add_task_to_workflow(wf_id, t2)
    manager.add_task_to_workflow(wf_id, t3)

    manager.run_workflow(wf_id)
    assert order == ["a", "b", "c"]

def test_workflow_failure_stops_subsequent():
    manager = WorkflowManager()
    wf_id = manager.register_workflow("wf2")
    order = []

    def a():
        order.append("a")
    def b():
        order.append("b")
        raise RuntimeError("fail")
    def c():
        order.append("c")

    manager.add_task_to_workflow(wf_id, Task("a", a))
    manager.add_task_to_workflow(wf_id, Task("b", b, dependencies=["a"]))
    manager.add_task_to_workflow(wf_id, Task("c", c, dependencies=["b"]))

    manager.run_workflow(wf_id)
    # 'c' should not run because 'b' failed
    assert order == ["a", "b"]
    wf = manager.get_workflow(wf_id)
    statuses = {tid: wf.tasks[tid].status for tid in wf.tasks}
    assert statuses["a"] == "SUCCESS"
    assert statuses["b"] == "FAILED"
    assert statuses["c"] == "PENDING"