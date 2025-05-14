import time
import pytest
from sre.task_queue.queue import TaskQueue, CircuitOpen, TaskNotFound, DependencyFailed
from sre.task_queue.task import Task

def test_enqueue_and_complete():
    tq = TaskQueue()
    tq.adjust_quota('svc', 1)
    tid = tq.enqueue('T1', 'svc', {'job':'hchk'})
    assert len(tq.list_active('T1')) == 1
    # no ready immediately if no delay
    ready = tq.get_ready_tasks()
    assert any(t.id == tid for t in ready)
    tq.complete(tid)
    assert len(tq.list_active('T1')) == 0
    with pytest.raises(TaskNotFound):
        tq.complete('nonexistent')

def test_quota_enforcement():
    tq = TaskQueue()
    tq.adjust_quota('svc', 1)
    tid1 = tq.enqueue('T', 'svc', {})
    with pytest.raises(Exception):
        tq.enqueue('T', 'svc', {})  # second should exceed

def test_cancel():
    tq = TaskQueue()
    tq.adjust_quota('svc', 1)
    tid = tq.enqueue('T', 'svc', {})
    tq.cancel(tid)
    assert len(tq.list_active('T')) == 0

def test_retry_and_fail():
    tq = TaskQueue()
    tq.adjust_quota('svc', 1)
    tid = tq.enqueue('T', 'svc', {}, max_retries=1)
    # simulate fail twice
    ok = tq.fail(tid)
    assert ok  # first retry
    ok2 = tq.fail(tid)
    assert ok2 is False
    assert len(tq.list_active('T')) == 0

def test_circuit_open_on_enqueue():
    tq = TaskQueue()
    # open circuit manually
    svc = 'ext'
    for _ in range(3):
        tq.cb.record_failure(svc)
    with pytest.raises(CircuitOpen):
        tq.enqueue('T', svc, {})

def test_dependency_handling():
    tq = TaskQueue()
    tq.adjust_quota('svc', 2)
    p1 = tq.enqueue('T', 'svc', {})
    p2 = tq.enqueue('T', 'svc', {}, dependencies=[p1])
    # p2 not ready until p1 complete
    ready = tq.get_ready_tasks()
    ids = [t.id for t in ready]
    assert p1 in ids and p2 not in ids
    tq.complete(p1)
    ready2 = tq.get_ready_tasks()
    assert any(t.id == p2 for t in ready2)
    # failing parent should prevent child
    p3 = tq.enqueue('T', 'svc', {})
    p4 = tq.enqueue('T', 'svc', {}, dependencies=[p3])
    tq.fail(p3)
    with pytest.raises(DependencyFailed):
        tq.enqueue('T', 'svc', {}, dependencies=[p3])

def test_delayed_scheduling():
    tq = TaskQueue()
    tq.adjust_quota('svc', 1)
    tid = tq.enqueue('T', 'svc', {}, delay=0.5)
    ready1 = tq.get_ready_tasks(time.time())
    assert tid not in [t.id for t in ready1]
    time.sleep(0.6)
    ready2 = tq.get_ready_tasks(time.time())
    assert tid in [t.id for t in ready2]

def test_multi_tenancy_isolated():
    tq = TaskQueue()
    tq.adjust_quota('s', 2)
    t1 = tq.enqueue('A', 's', {})
    t2 = tq.enqueue('B', 's', {})
    assert len(tq.list_active('A')) == 1
    assert len(tq.list_active('B')) == 1

def test_encrypt_state_roundtrip():
    tq = TaskQueue()
    data = b'some_state'
    token = tq.encrypt_state(data)
    assert token != data
    assert tq.decrypt_state(token) == data
