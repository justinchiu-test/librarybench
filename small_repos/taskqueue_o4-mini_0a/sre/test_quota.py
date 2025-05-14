import pytest
from task_queue.quota import QuotaManager, QuotaExceeded

def test_quota_basic():
    q = QuotaManager()
    assert q.can_use('svc')
    q.set_quota('svc', 2)
    assert q.get_quota('svc') == 2
    q.use('svc')
    q.use('svc')
    with pytest.raises(QuotaExceeded):
        q.use('svc')
    assert q.get_usage('svc') == 2
    q.release('svc')
    assert q.get_usage('svc') == 1
