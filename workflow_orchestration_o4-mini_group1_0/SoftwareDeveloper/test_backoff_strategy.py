import pytest
from SoftwareDeveloper.tasks.task import Task
from SoftwareDeveloper.tasks.executor import TaskExecutor

def test_exponential_backoff():
    calls = []
    # dummy sleep to capture delays
    def fake_sleep(sec):
        calls.append(sec)

    # always fail
    def bad(ctx):
        raise ValueError("x")

    executor = TaskExecutor(sleep_func=fake_sleep)
    t = Task(name="bad2",
             func=bad,
             max_retries=2,
             retry_delay_seconds=1,
             backoff_factor=2)
    executor.register_task(t)

    with pytest.raises(Exception):
        executor.execute("bad2")

    # we expect two retry delays: after attempt1 and attempt2
    # delays: 1 * 2^(1-1)=1, then 1 * 2^(2-1)=2
    assert calls == [1, 2]
