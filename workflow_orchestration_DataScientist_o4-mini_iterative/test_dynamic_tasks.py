import pytest
from pipeline.task import Task
from pipeline.pipeline import Pipeline
from pipeline.context import ExecutionContext
from pipeline.metadata import MetadataStorage
from pipeline.notifier import DummyNotifier

def test_dynamic_task_creation_and_execution():
    ctx = ExecutionContext()
    meta = MetadataStorage()
    notifier = DummyNotifier()

    # Preload a list of items in context
    ctx.set('items', [1, 2, 3])

    # Creator task: generates processing tasks for each item
    def creator(context):
        items = context.get('items')
        new_tasks = []
        for item in items:
            def make_func(i):
                def proc(ctx):
                    return {f'item_{i}': i * 2}
                return proc
            t = Task(
                name=f'proc_{item}',
                func=make_func(item),
                outputs=[f'item_{item}']
            )
            new_tasks.append(t)
        return new_tasks

    creator_task = Task(name='creator', func=creator, inputs=['items'])
    pipeline = Pipeline([creator_task], ctx, meta, notifier)
    pipeline.run()

    # After run, dynamic tasks should have executed
    for i in [1,2,3]:
        assert ctx.get(f'item_{i}') == i * 2
        rec = meta.get_all(f'proc_{i}')[0]
        assert rec['status'] == 'success'
    # Creator also succeeded
    assert creator_task.state == 'success'
