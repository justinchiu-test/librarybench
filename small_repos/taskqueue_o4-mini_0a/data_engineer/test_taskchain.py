import pytest
import datetime
from etl.taskchain import Task, TaskChaining

def dummy():
    return 1

def test_task_chaining_and_ready():
    tc = TaskChaining()
    t1 = Task("t1", dummy)
    t2 = Task("t2", dummy, dependencies=["t1"])
    tc.add_task(t1)
    tc.add_task(t2)
    ready = tc.get_ready_tasks()
    assert t1 in ready
    tc.mark_completed("t1")
    ready2 = tc.get_ready_tasks()
    assert t2 in ready2
    tc.mark_completed("t2")
    ready3 = tc.get_ready_tasks()
    assert ready3 == []
