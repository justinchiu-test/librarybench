import pytest
import time
from pipeline.task import Task, TaskTimeoutError
from pipeline.pipeline import Pipeline

class SlowTask(Task):
    def __init__(self, task_id, sleep_time, **kwargs):
        super().__init__(task_id, **kwargs)
        self.sleep_time = sleep_time

    def run(self, context):
        time.sleep(self.sleep_time)
        return "finished"

def test_task_timeout():
    task = SlowTask("slow1", sleep_time=0.2, timeout_seconds=0.1)
    p = Pipeline()
    p.add_task(task)
    ctx = p.run()
    # should have recorded failure state
    assert task.state == 'failure'
    # alert was sent
    assert len(p.alerting.notifications) == 1
    assert "timed out" in p.alerting.notifications[0]
