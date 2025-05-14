import time
from retry.history import RetryHistoryCollector

def test_history_collector():
    hist = RetryHistoryCollector()
    t = time.time()
    hist.record(1, 0, None, t, True)
    hist.record(2, 1, Exception("err"), t+1, False)
    assert len(hist.history) == 2
    assert hist.history[0]['success'] is True
    assert hist.history[1]['success'] is False
