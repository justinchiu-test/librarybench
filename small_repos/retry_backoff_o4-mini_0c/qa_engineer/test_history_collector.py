import pytest
from retry_toolkit.history_collector import RetryHistoryCollector

def test_successful_calls_are_recorded():
    collector = RetryHistoryCollector()
    @collector.record
    def foo(x, y=0):
        return x + y
    assert foo(2, y=3) == 5
    history = collector.get_history()
    assert len(history) == 1
    entry = history[0]
    assert entry["result"] == 5
    assert "exception" not in entry

def test_exception_calls_are_recorded():
    collector = RetryHistoryCollector()
    @collector.record
    def bar():
        raise ValueError("oops")
    with pytest.raises(ValueError):
        bar()
    history = collector.get_history()
    assert len(history) == 1
    entry = history[0]
    assert isinstance(entry["exception"], ValueError)
    assert "result" not in entry
