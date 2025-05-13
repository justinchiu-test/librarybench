import pytest
import time
from metrics import MetricsIntegration
from quota import QuotaManagement, QuotaExceeded
from tenant import MultiTenancySupport, TenantContext
from circuit_breaker import CircuitBreaker, CircuitOpen
from audit import AuditLogger
from scheduler import Scheduler
from encryption import EncryptionManager
from queue import TaskQueue

def build_components():
    m = MetricsIntegration()
    q = QuotaManagement(merchant_limit=1000, customer_limit=1000)
    t = MultiTenancySupport()
    cb = CircuitBreaker(failure_threshold=1)
    a = AuditLogger()
    s = Scheduler()
    e = EncryptionManager(key=b"k")
    return m, q, t, cb, a, s, e

def test_successful_enqueue_and_process():
    m, q, t, cb, a, s, e = build_components()
    queue = TaskQueue(m, q, t, cb, a, s, e)
    queue.enqueue("card", 10, "m1", "c1", "t1", binary_payload=b"data")
    # No delay; should process immediately
    logs = a.get_logs()
    actions = [entry["action"] for entry in logs]
    assert "enqueue" in actions
    assert "fraud_check_start" in actions
    assert "settlement_complete" in actions
    met = m.get_metrics("card")
    assert met["throughput"] == 1

def test_quota_exceeded_enqueue():
    m, q, t, cb, a, s, e = build_components()
    q = QuotaManagement(merchant_limit=5, customer_limit=5)
    queue = TaskQueue(m, q, t, cb, a, s, e)
    with pytest.raises(QuotaExceeded):
        queue.enqueue("card", 10, "m1", "c1", "t1")

def test_circuit_breaker_blocks():
    m, q, t, cb, a, s, e = build_components()
    # Make fraud API fail
    def bad_fraud(pt):
        raise ValueError("bad")
    queue = TaskQueue(m, q, t, cb, a, s, e)
    queue._fake_fraud_api = bad_fraud
    with pytest.raises(ValueError):
        queue.enqueue("card", 1, "m", "c", "t", binary_payload=None)
    # circuit now open (threshold=1)
    with pytest.raises(CircuitOpen):
        queue.enqueue("card", 1, "m", "c", "t", binary_payload=None)

def test_delayed_enqueue():
    m, q, t, cb, a, s, e = build_components()
    queue = TaskQueue(m, q, t, cb, a, s, e)
    run_at = time.time() + 1
    queue.enqueue("card", 1, "m1", "c1", "t1", delay_until=run_at)
    # not yet run
    assert s._queue
    s.run_due()
    # still not run
    assert s._queue
    time.sleep(1.1)
    s.run_due()
    logs = a.get_logs()
    actions = [entry["action"] for entry in logs]
    assert "enqueue" in actions
    assert "settlement_complete" in actions

def test_queue_health_and_replay():
    m, q, t, cb, a, s, e = build_components()
    queue = TaskQueue(m, q, t, cb, a, s, e)
    # force a failed task
    def bad(pt):
        raise ValueError("bad")
    queue._fake_fraud_api = bad
    with pytest.raises(ValueError):
        queue.enqueue("card", 1, "m", "c", "t", binary_payload=None)
    health = queue.queue_health()
    assert len(health["failed_tasks"]) == 1
    replayed = queue.replay_failed()
    assert len(replayed) == 1
    # replay clears failed
    health2 = queue.queue_health()
    assert len(health2["failed_tasks"]) == 0
