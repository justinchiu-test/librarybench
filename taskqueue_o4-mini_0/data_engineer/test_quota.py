import pytest
from etl.quota import QuotaManagement, QuotaExceededError

def test_quota_within_limits():
    q = QuotaManagement(cpu_quota=100, memory_quota=200)
    q.consume(10, 20)
    q.consume(30, 50)
    assert q.cpu_used == 40
    assert q.memory_used == 70

def test_quota_exceeded():
    q = QuotaManagement(cpu_quota=10, memory_quota=10)
    with pytest.raises(QuotaExceededError):
        q.consume(5, 6)
        q.consume(6, 5)

def test_quota_reset():
    q = QuotaManagement(cpu_quota=10, memory_quota=10)
    q.consume(5, 5)
    q.reset()
    assert q.cpu_used == 0
    assert q.memory_used == 0
