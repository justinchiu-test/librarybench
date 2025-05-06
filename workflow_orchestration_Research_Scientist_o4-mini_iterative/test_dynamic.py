import pytest
from workflow.manager import TaskManager
from workflow.models import Task, RetryPolicy, TaskState

def dynamic_creator(manager, prefix):
    # create a new simple task
    def new_task():
        return prefix + "_child"
    child = Task(id=prefix+"_child", func=new_task, args=(), priority=1,
                 retry_policy=RetryPolicy())
    manager.add_task(child)
    return prefix + "_parent"

def test_dynamic_task_creation(monkeypatch):
    manager = TaskManager()
    # Create a task that generates another task
    parent = Task(id='p1', func=dynamic_creator,
                  args=(manager, 'p1'), priority=2,
                  retry_policy=RetryPolicy())
    monkeypatch.setattr(__import__('time'), 'sleep', lambda x: None)
    manager.add_task(parent)
    manager.run_all()
    # parent should have succeeded
    p = manager.get_task('p1')
    assert p.state == TaskState.SUCCESS
    assert p.result == 'p1_parent'
    # child should exist and be pending, now run it
    c = manager.get_task('p1_child')
    assert c is not None
    assert c.state == TaskState.PENDING
    manager.run_all()
    c = manager.get_task('p1_child')
    assert c.state == TaskState.SUCCESS
    assert c.result == 'p1_child'
