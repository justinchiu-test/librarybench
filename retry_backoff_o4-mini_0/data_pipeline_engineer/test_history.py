import time
from retrylib.history import RetryHistoryCollector
from retrylib.context import ContextPropagation

def test_retry_history_collector_records():
    history = RetryHistoryCollector()
    ctx = ContextPropagation(x=42)
    t0 = time.time()
    history.record(1, 0.5, Exception("err"), t0, ctx)
    assert len(history.attempts) == 1
    rec = history.attempts[0]
    assert rec['attempt'] == 1
    assert rec['delay'] == 0.5
    assert isinstance(rec['exception'], Exception)
    assert rec['timestamp'] == t0
    assert rec['context'].get('x') == 42
