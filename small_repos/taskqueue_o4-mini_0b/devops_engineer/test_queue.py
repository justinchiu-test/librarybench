import time
import pytest
from taskqueue.queue import TaskQueue

def test_enqueue_and_unique_ids():
    q = TaskQueue()
    ids = set()
    for i in range(10):
        tid = q.enqueue(f'payload{i}')
        assert tid not in ids
        ids.add(tid)
    assert q.metrics['enqueued'] == 10
    stats = q.get_stats()
    assert stats['pending'] == 10

def test_delayed_task_scheduling():
    q = TaskQueue()
    tid1 = q.enqueue('p1', delay=1)
    tid2 = q.enqueue('p2', delay=0)
    ready = q.get_ready_tasks()
    ids = [t.id for t in ready]
    assert tid2 in ids and tid1 not in ids
    time.sleep(1.1)
    ready2 = q.get_ready_tasks()
    ids2 = [t.id for t in ready2]
    assert tid1 in ids2

def test_dequeue_and_finish():
    q = TaskQueue()
    tid = q.enqueue('p')
    task = q.dequeue()
    assert task.id == tid
    q.finish(task)
    stats = q.get_stats()
    assert stats['finished'] == 1
    metrics = q.get_metrics()
    assert 'task_processed_total 1' in metrics

def test_fail_and_dlq():
    q = TaskQueue()
    tid = q.enqueue('p', max_retries=1)
    task = q.dequeue()
    q.fail(task)
    assert task.status == 'pending'
    task2 = q.dequeue()
    q.fail(task2)
    assert task2 in q.dlq
    stats = q.get_stats()
    assert stats['dlq'] == 1

def test_cancel():
    q = TaskQueue()
    tid = q.enqueue('p')
    ok = q.cancel(tid)
    assert ok
    stats = q.get_stats()
    assert stats['pending'] == 0
    assert q.metrics['canceled'] == 1

def test_shutdown_prevents_enqueue():
    q = TaskQueue()
    q.shutdown()
    with pytest.raises(RuntimeError):
        q.enqueue('p')

def test_snapshot_and_restore(tmp_path):
    q = TaskQueue(data_dir=str(tmp_path))
    tid = q.enqueue('p')
    task = q.dequeue()
    q.finish(task)
    snap = tmp_path / 'snap.bin'
    q.snapshot(str(snap))
    q.enqueue('x')
    q2 = TaskQueue.restore(str(snap), data_dir=str(tmp_path))
    stats = q2.get_stats()
    assert stats['finished'] == 1
    assert stats['pending'] == 0
