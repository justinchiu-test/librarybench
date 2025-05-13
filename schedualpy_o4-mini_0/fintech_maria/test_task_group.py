import pytest
from scheduler.task_group import TaskGroupManager

def test_task_group_manager():
    mgr = TaskGroupManager()
    mgr.create_task_group('settlement', ['j1', 'j2'])
    assert mgr.get_group('settlement') == {'j1', 'j2'}
    mgr.add_job('settlement', 'j3')
    assert 'j3' in mgr.get_group('settlement')
    mgr.remove_job('settlement', 'j2')
    assert 'j2' not in mgr.get_group('settlement')
    mgr.delete_group('settlement')
    assert mgr.get_group('settlement') == set()
