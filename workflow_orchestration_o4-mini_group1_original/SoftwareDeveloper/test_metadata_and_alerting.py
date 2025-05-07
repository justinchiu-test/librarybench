import pytest
from SoftwareDeveloper.tasks.task import Task
from SoftwareDeveloper.tasks.executor import TaskExecutor
from SoftwareDeveloper.tasks.metadata import MetadataStorage
from SoftwareDeveloper.tasks.alerting import AlertingService

def test_metadata_records_and_alert_payload():
    calls = {'n':0}
    def sometimes(ctx):
        calls['n'] += 1
        if calls['n'] == 1:
            raise KeyError("first")
        return {"x": 5}

    meta = MetadataStorage()
    alert = AlertingService()
    executor = TaskExecutor(metadata_storage=meta, alerting_service=alert)

    t = Task(name="maybe",
             func=sometimes,
             input_keys=[],
             output_keys=['x'],
             max_retries=1,
             retry_delay_seconds=0)
    executor.register_task(t)

    res = executor.execute("maybe")
    assert res == {"x":5}
    # two metadata entries: 1 fail, 1 success
    recs = meta.get("maybe")
    assert len(recs) == 2
    assert recs[0]['exception'].__class__ is KeyError
    assert recs[1]['status'].name == "SUCCESS"
    # alerting: only on final failure; here we succeeded so no alerts
    assert alert.alerts == []

    # now force total failure
    def always_bad(ctx):
        raise RuntimeError("nope")
    t2 = Task(name="always",
              func=always_bad,
              max_retries=0)
    executor.register_task(t2)
    with pytest.raises(Exception):
        executor.execute("always")
    # metadata 1 entry
    assert len(meta.get("always")) == 1
    # we get one alert
    assert len(alert.alerts) == 1
    a = alert.alerts[-1]
    assert a['task_name'] == "always"
    assert isinstance(a['exception'], RuntimeError)
