import time
import pytest
from pipeline.task import Task
from pipeline.pipeline import Pipeline
from pipeline.context import ExecutionContext
from pipeline.metadata import MetadataStorage
from pipeline.notifier import DummyNotifier

def test_retry_with_exponential_backoff(monkeypatch):
    ctx = ExecutionContext()
    meta = MetadataStorage()
    notifier = DummyNotifier()

    # Create a flaky task that fails twice then succeeds
    attempts = {'count': 0}
    delays = []

    def flaky(context):
        attempts['count'] += 1
        if attempts['count'] < 3:
            raise ValueError("Intermittent failure")
        return {'x': 42}

    # Monkeypatch time.sleep to record delays without real waiting
    def fake_sleep(d):
        delays.append(d)
    monkeypatch.setattr(time, 'sleep', fake_sleep)

    t = Task(
        name='flaky',
        func=flaky,
        outputs=['x'],
        max_retries=4,
        retry_delay_seconds=1,
        backoff=True,
        timeout=None
    )
    pipeline = Pipeline([t], ctx, meta, notifier)
    pipeline.run()

    # Should have succeeded
    assert t.state == 'success'
    assert ctx.get('x') == 42
    # It should have taken 3 attempts
    rec = meta.get_all('flaky')[0]
    assert rec['attempts'] == 3
    # Exponential backoff delays: attempt1->fail no sleep before, attempt2->sleep 1*(2**(2-1))=2, attempt3->no more sleep since success
    # Actually first failure attempt1, attempt=1, sleep base*(2**0)=1 ; second failure attempt2 sleep base*(2**1)=2.
    assert delays == [1, 2]
    # No failure alerts
    assert notifier.messages == []
