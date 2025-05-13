import pytest
from scheduler.distributed_execution import DistributedExecution

def test_consume_success():
    de = DistributedExecution()
    results = []
    de.produce("job1")
    def cb(job):
        results.append(job)
    returned = de.consume(cb)
    assert returned == "job1"
    assert results == ["job1"]
    # no more jobs
    assert de.consume(cb) is None

def test_consume_failure_and_retry():
    de = DistributedExecution()
    de.produce("job2")
    # first callback fails
    def cb_fail(job):
        raise ValueError("fail")
    with pytest.raises(ValueError):
        de.consume(cb_fail)
    # second consume should requeue and succeed
    results = []
    def cb_ok(job):
        results.append(job)
    returned = de.consume(cb_ok)
    assert returned == "job2"
    assert results == ["job2"]
    assert de.consume(cb_ok) is None
