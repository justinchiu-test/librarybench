import pytest
from sre.task_queue.multitenancy import MultiTenantQueue, QueuePaused

def test_multi_tenant():
    mt = MultiTenantQueue()
    mt.add_task('A', 't1')
    mt.add_task('B', 't2')
    assert mt.list_tasks('A') == ['t1']
    assert sorted(mt.list_tasks()) == ['t1', 't2']
    mt.pause('A')
    with pytest.raises(QueuePaused):
        mt.add_task('A', 't3')
    mt.resume('A')
    mt.add_task('A', 't3')
    assert mt.list_tasks('A') == ['t1', 't3']
    mt.remove_task('A', 't1')
    assert mt.list_tasks('A') == ['t3']
