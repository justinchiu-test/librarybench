import pytest
from tasks.task import Task
from tasks.executor import TaskExecutor
from tasks.context import ExecutionContext
from tasks.metadata import MetadataStorage

def test_simple_success():
    # A task that adds two numbers
    def add(ctx, x, y):
        return {'z': x + y}

    ctx = ExecutionContext({'x': 2, 'y': 3})
    meta = MetadataStorage()
    executor = TaskExecutor(context=ctx, metadata_storage=meta)

    t = Task(name="add", func=add, input_keys=['x','y'], output_keys=['z'])
    executor.register_task(t)

    result = executor.execute("add")
    # result should be dict with z
    assert isinstance(result, dict)
    assert result['z'] == 5
    # context updated
    assert ctx['z'] == 5
    # metadata recorded
    recs = meta.get("add")
    assert len(recs) == 1
    m0 = recs[0]
    assert m0['status'].name == "SUCCESS"
    assert m0['retries'] == 0
    assert m0['execution_time'] >= 0
