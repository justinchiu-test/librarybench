import pytest
import time
from pipeline.task import Task
from pipeline.pipeline import Pipeline
from pipeline.context import ExecutionContext
from pipeline.metadata import MetadataStorage
from pipeline.notifier import DummyNotifier

def test_task_timeout_and_retry(monkeypatch):
    ctx = ExecutionContext()
    meta = MetadataStorage()
    notifier = DummyNotifier()

    # A task that sleeps longer than its timeout
    def slow_task(context):
        time.sleep(0.1)
        return {'y': 'done'}

    # Monkeypatch time.sleep so that slow_task actually runs real sleep,
    # but pipeline retry waits are no-ops
    original_sleep = time.sleep
    def fake_sleep(d):
        # only fake small waits
        if d < 0.05:
            return
        original_sleep(d)
    monkeypatch.setattr(time, 'sleep', fake_sleep)

    t = Task(
        name='slow',
        func=slow_task,
        outputs=['y'],
        max_retries=1,
        retry_delay_seconds=0.01,
        backoff=False,
        timeout=0.05
    )
    pipeline = Pipeline([t], ctx, meta, notifier)
    pipeline.run()

    # Task should have failed
    assert t.state == 'failure'
    # Metadata: two attempts (initial + one retry)
    rec = meta.get_all('slow')[0]
    assert rec['attempts'] == 2
    assert rec['status'] == 'failure'
    # No output set
    assert ctx.get('y') is None
    # Notifier alerted
    assert len(notifier.messages) == 1
    assert 'timed out' in notifier.messages[0]
