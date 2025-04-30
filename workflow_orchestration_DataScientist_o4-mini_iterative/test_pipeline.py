import pytest
from pipeline.task import Task
from pipeline.pipeline import Pipeline
from pipeline.context import ExecutionContext
from pipeline.metadata import MetadataStorage
from pipeline.notifier import DummyNotifier

def test_basic_pipeline_execution_and_data_passing():
    ctx = ExecutionContext()
    meta = MetadataStorage()
    notifier = DummyNotifier()

    def task1(context):
        # produce 'a' = 1
        return {'a': 1}

    def task2(context):
        a = context.get('a')
        return {'b': a + 1}

    t1 = Task(name='t1', func=task1, outputs=['a'])
    t2 = Task(name='t2', func=task2, inputs=['a'], outputs=['b'])
    pipeline = Pipeline([t1, t2], ctx, meta, notifier)
    pipeline.run()

    # Check context values
    assert ctx.get('a') == 1
    assert ctx.get('b') == 2

    # Check states
    assert t1.state == 'success'
    assert t2.state == 'success'

    # Metadata recorded
    rec1 = meta.get_all('t1')
    rec2 = meta.get_all('t2')
    assert len(rec1) == 1
    assert rec1[0]['status'] == 'success'
    assert rec1[0]['attempts'] == 1
    assert len(rec2) == 1
    assert rec2[0]['status'] == 'success'
    assert rec2[0]['attempts'] == 1

    # No alerts sent
    assert notifier.messages == []
