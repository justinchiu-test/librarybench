import pytest
from scheduler.workflow import Workflow

def test_successful_workflow():
    wf = Workflow()
    wf.add_step(lambda x: x + 1)
    wf.add_step(lambda x: x * 2)
    result = wf.run(3)
    assert result == (3 + 1) * 2

def test_retry_on_exception():
    counter = {'calls': 0}
    def flaky(x):
        counter['calls'] += 1
        if counter['calls'] < 2:
            raise RuntimeError("temporarily down")
        return x + 10
    wf = Workflow()
    wf.add_step(flaky, retry_on_exception=(RuntimeError,), max_retries=3)
    result = wf.run(5)
    assert result == 15
    assert counter['calls'] == 2

def test_retry_exhaustion():
    def always_fail(x):
        raise RuntimeError("oops")
    wf = Workflow()
    wf.add_step(always_fail, retry_on_exception=(RuntimeError,), max_retries=1)
    with pytest.raises(RuntimeError):
        wf.run(0)
