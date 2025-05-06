import pytest
import time
from DataScientist.pipeline.task import Task, TaskFailureError
from DataScientist.pipeline.pipeline import Pipeline

class IntermittentTask(Task):
    def __init__(self, task_id, fails_before_success, **kwargs):
        super().__init__(task_id, **kwargs)
        self._fails = fails_before_success
        # override sleep to avoid real delay
        self._sleep = lambda x: None

    def run(self, context):
        if self._fails > 0:
            self._fails -= 1
            raise ValueError("temporary failure")
        return "ok"

def test_retry_success():
    task = IntermittentTask("it1", fails_before_success=2, max_retries=3, retry_delay_seconds=0.1, backoff_factor=2)
    p = Pipeline()
    p.add_task(task)
    ctx = p.run()
    assert task.state == 'success'
    assert task.attempt == 3
    assert ctx.get("it1") == "ok"

def test_retry_failure():
    task = IntermittentTask("it2", fails_before_success=5, max_retries=2, retry_delay_seconds=0.1, backoff_factor=2)
    p = Pipeline()
    p.add_task(task)
    with pytest.raises(Exception):
        # pipeline.run swallows the exception internally and continues, so we run execute directly
        task.execute(p.context)
    assert task.state == 'failure'
