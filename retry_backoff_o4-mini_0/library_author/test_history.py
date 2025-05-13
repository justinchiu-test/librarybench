import pytest
from retry_framework.history import RetryHistoryCollector

def test_record_and_get_history():
    collector = RetryHistoryCollector()
    assert collector.get_history() == []
    collector.record({"attempt": 1})
    collector.record({"attempt": 2})
    history = collector.get_history()
    assert len(history) == 2
    assert history[0] == {"attempt": 1}
    assert history[1] == {"attempt": 2}
