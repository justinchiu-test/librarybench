import pytest
from DataScientist.pipeline.task import Task
from DataScientist.pipeline.pipeline import Pipeline

class DummyTask(Task):
    def run(self, context):
        return "done"

def test_task_state_transitions():
    task = DummyTask("t1")
    assert task.state == 'pending'
    # wrap in pipeline to run
    p = Pipeline()
    p.add_task(task)
    ctx = p.run()
    assert task.state == 'success'
    assert ctx.get("t1") == "done"
