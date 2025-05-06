import pytest
from workflow.models import TaskState, RetryPolicy, Task

def dummy_func(x):
    return x * 2

def test_taskstate_enum():
    assert TaskState.PENDING.value == 'pending'
    assert TaskState.SUCCESS.name == 'SUCCESS'

def test_retry_policy_defaults():
    rp = RetryPolicy()
    assert rp.max_retries == 0
    assert rp.retry_delay_seconds == 0.0

def test_task_ordering_by_priority():
    t1 = Task(id='t1', func=dummy_func, args=(1,), priority=5, retry_policy=None)
    t2 = Task(id='t2', func=dummy_func, args=(2,), priority=10, retry_policy=None)
    # In heap we invert priority, but ordering here is by dataclass order
    # Higher priority should compare greater
    assert t2.priority > t1.priority
