import time
from retry_framework.history import RetryHistoryCollector

def test_record():
    hist = RetryHistoryCollector()
    hist.record(time.time(), 0.5, None, True)
    hist.record(time.time(), 1.0, Exception('err'), False)
    assert len(hist.attempts) == 2
    assert hist.attempts[0]['outcome'] is True
    assert hist.attempts[1]['outcome'] is False
