import pytest
from task_manager.task import Task
from task_manager.workflow import Workflow, WorkflowManager

def tA(): return "A"
def tB(): return "B"
def tC(): return "C"

def test_dependency_order():
    a = Task("A", tA)
    b = Task("B", tB)
    c = Task("C", tC)
    c.add_dependency(a)
    c.add_dependency(b)
    wf = Workflow("wf")
    wf.add_task(a)
    wf.add_task(b)
    wf.add_task(c)
    res = wf.run()
    assert res == {"A": "A", "B": "B", "C": "C"}

def test_versioning():
    wm = WorkflowManager()
    w1 = Workflow("X")
    w2 = Workflow("X")
    wm.register(w1)
    wm.register(w2)
    assert w1.version == 1
    assert w2.version == 2
    assert wm.get("X",1) is w1
    assert wm.get_latest("X") is w2
    assert wm.get("X",3) is None
