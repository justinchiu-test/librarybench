import pytest
from scheduler.priority import JobPriorityQueue

def test_priority_queue_order():
    pq = JobPriorityQueue()
    pq.push('low', priority=10)
    pq.push('high', priority=1)
    pq.push('medium', priority=5)
    assert len(pq) == 3
    assert pq.pop() == 'high'
    assert pq.pop() == 'medium'
    assert pq.pop() == 'low'
    with pytest.raises(IndexError):
        pq.pop()
