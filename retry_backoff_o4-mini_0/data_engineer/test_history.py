import pytest
from retry_toolkit.history import RetryHistoryCollector

def test_record_history():
    rh = RetryHistoryCollector()
    rh.record(1, False, 0.1, Exception("fail"))
    rh.record(2, True, 0.2, None)
    hist = rh.get_history()
    assert len(hist) == 2
    assert hist[0]['attempt'] == 1
    assert hist[0]['success'] is False
    assert isinstance(hist[0]['exception'], Exception)
    assert hist[1]['success'] is True
