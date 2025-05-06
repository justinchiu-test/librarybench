import pytest
from SoftwareDeveloper.tasks.task import Task
from SoftwareDeveloper.tasks.executor import TaskExecutor, TaskExecutionError
from SoftwareDeveloper.tasks.metadata import MetadataStorage

def test_retry_and_success():
    # a flaky task: fails once, then succeeds
    def flaky(ctx):
        count = ctx.get('count', 0) + 1
        ctx['count'] = count
        if count < 2:
            raise ValueError("oops")
        return {'out': 99}

    meta = MetadataStorage()
    executor = TaskExecutor(metadata_storage=meta, context={})

    t = Task(name="flaky",
             func=flaky,
             input_keys=[],
             output_keys=['out'],
             max_retries=1,
             retry_delay_seconds=0)
    executor.register_task(t)

    res = executor.execute("flaky")
    assert res == {'out': 99}
    # metadata: two attempts, first failure, second success
    recs = meta.get("flaky")
    assert len(recs) == 2
    # first attempt
    assert recs[0]['status'].name == "RUNNING"
    assert isinstance(recs[0]['exception'], ValueError)
    # second attempt success
    assert recs[1]['status'].name == "SUCCESS"
    assert recs[1]['retries'] == 1

def test_always_fail_and_alert():
    def always_fail(ctx):
        raise RuntimeError("bad")

    from tasks.alerting import AlertingService
    alert = AlertingService()
    meta = MetadataStorage()
    executor = TaskExecutor(metadata_storage=meta, alerting_service=alert)

    t = Task(name="bad",
             func=always_fail,
             max_retries=2,
             retry_delay_seconds=0)
    executor.register_task(t)

    with pytest.raises(TaskExecutionError) as ei:
        executor.execute("bad")

    # three attempts total: retries=2 => attempts=3
    recs = meta.get("bad")
    assert len(recs) == 3
    # the final exception should be RuntimeError
    assert isinstance(ei.value.original_exception, RuntimeError)
    # an alert should have been sent once
    assert len(alert.alerts) == 1
    a = alert.alerts[0]
    assert a['task_name'] == "bad"
    assert isinstance(a['exception'], RuntimeError)
