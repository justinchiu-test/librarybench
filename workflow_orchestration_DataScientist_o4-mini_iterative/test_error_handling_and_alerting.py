import pytest
from pipeline.task import Task
from pipeline.pipeline import Pipeline
from pipeline.context import ExecutionContext
from pipeline.metadata import MetadataStorage
from pipeline.notifier import DummyNotifier

def test_unexpected_exception_triggers_alert():
    ctx = ExecutionContext()
    meta = MetadataStorage()
    notifier = DummyNotifier()

    def bad_task(context):
        # raises unexpected error
        raise KeyError("Oops!")

    t = Task(
        name='bad',
        func=bad_task,
        max_retries=0,
        retry_delay_seconds=0,
        backoff=False
    )
    pipeline = Pipeline([t], ctx, meta, notifier)
    pipeline.run()

    # Task failed
    assert t.state == 'failure'
    rec = meta.get_all('bad')[0]
    assert rec['attempts'] == 1
    assert rec['status'] == 'failure'
    # Notifier should have one message
    assert len(notifier.messages) == 1
    assert 'bad' in notifier.messages[0]
    assert 'Oops' in notifier.messages[0]
