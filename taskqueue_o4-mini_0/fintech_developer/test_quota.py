import pytest
from quota import QuotaManagement, QuotaExceeded

def test_quota_within_limits():
    q = QuotaManagement(merchant_limit=100, customer_limit=50)
    q.check_and_consume("m1", "c1", 30)
    q.check_and_consume("m1", "c1", 20)
    # Now merchant=50, customer=50
    with pytest.raises(QuotaExceeded):
        q.check_and_consume("m1", "c1", 1)

def test_quota_reset():
    q = QuotaManagement(merchant_limit=10, customer_limit=10)
    q.check_and_consume("m", "c", 10)
    with pytest.raises(QuotaExceeded):
        q.check_and_consume("m", "c", 1)
    q.reset()
    q.check_and_consume("m", "c", 10)
