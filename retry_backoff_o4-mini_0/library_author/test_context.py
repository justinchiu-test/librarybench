import pytest
import time
from retry_framework.context import ContextManagerAPI
from retry_framework.history import RetryHistoryCollector

def test_context_manager_records_history():
    hist = RetryHistoryCollector()
    with ContextManagerAPI(history_collector=hist) as ctx:
        time.sleep(0.001)
    entries = hist.get_history()
    assert len(entries) == 2
    assert entries[0]["event"] == "enter"
    assert entries[1]["event"] == "exit"
    assert "duration" in entries[1]
    assert entries[1]["exception"] is None

def test_context_manager_propagates_exception():
    hist = RetryHistoryCollector()
    with pytest.raises(ValueError):
        with ContextManagerAPI(history_collector=hist):
            raise ValueError("oops")
    entries = hist.get_history()
    assert entries[1]["exception"] == "ValueError"
