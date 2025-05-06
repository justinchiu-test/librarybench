import pytest
from DataScientist.pipeline.task import Task
from DataScientist.pipeline.pipeline import Pipeline

class FailingTask(Task):
    def run(self, context):
        raise RuntimeError("oops")

def test_alert_on_failure():
    p = Pipeline()
    p.add_task(FailingTask("fail1"))
    ctx = p.run()
    # context will not have key
    assert ctx.get("fail1") is None
    # alert sent
    assert len(p.alerting.notifications) == 1
    assert "fail1" in p.alerting.notifications[0]
