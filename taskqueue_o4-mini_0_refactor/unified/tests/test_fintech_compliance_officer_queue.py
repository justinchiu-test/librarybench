import pytest
import time
import json
import uuid
from fintech_compliance_officer.queue import TaskQueue
from fintech_compliance_officer.encryption import decrypt

def test_unique_task_ids():
    q = TaskQueue('key')
    ids = set()
    for i in range(10):
        tid = q.enqueue({'val': i})
        # Valid UUID
        uuid.UUID(tid)
        ids.add(tid)
    assert len(ids) == 10

def test_encryption_at_rest():
    q = TaskQueue('key')
    payload = {'data': 'sensitive'}
    tid = q.enqueue(payload)
    raw_task = next(t for t in q.tasks if t['id'] == tid)
    assert 'encrypted_payload' in raw_task
    assert raw_task['encrypted_payload'] != json.dumps(payload)
    dec = decrypt(raw_task['encrypted_payload'], 'key')
    assert json.loads(dec) == payload

def test_delayed_task_scheduling(monkeypatch):
    q = TaskQueue('key')
    payload = {'x': 1}
    tid = q.enqueue(payload, delay=5)
    assert q.process_next() is None
    original_time = time.time()
    monkeypatch.setattr(time, 'time', lambda: original_time + 6)
    processed = q.process_next()
    assert processed is not None
    assert processed['id'] == tid

def test_backup_and_restore():
    q1 = TaskQueue('key')
    ids = [q1.enqueue({'n': i}) for i in range(3)]
    state = q1.backup()
    q2 = TaskQueue('key')
    q2.restore(state)
    assert [t['id'] for t in q1.tasks] == [t['id'] for t in q2.tasks]
    assert q2.get_metrics() == q1.get_metrics()
    assert q2.get_audit_log() == q1.get_audit_log()

def test_graceful_shutdown():
    q = TaskQueue('key')
    q.shutdown()
    q.enqueue({'a': 1})
    assert q.process_next() is None

def test_dead_letter_queue():
    q = TaskQueue('key')
    tid = q.enqueue({'fail': True})
    for _ in range(q.max_retries + 1):
        q.retry_task(tid)
    dl = q.get_dead_letter_queue()
    assert any(t['id'] == tid for t in dl)

def test_metrics_integration():
    q = TaskQueue('key')
    id1 = q.enqueue({'v': 1})
    id2 = q.enqueue({'v': 2})
    assert q.process_next()['id'] == id1
    assert q.process_next()['id'] == id2
    metrics = q.get_metrics()
    assert metrics['throughput'] == 2
    assert isinstance(metrics['latencies'], list)

def test_audit_logging():
    q = TaskQueue('key')
    tid = q.enqueue({'x': 1})
    q.process_next()
    logs = q.get_audit_log()
    events = [e['event'] for e in logs]
    assert 'enqueue' in events
    assert 'complete' in events
