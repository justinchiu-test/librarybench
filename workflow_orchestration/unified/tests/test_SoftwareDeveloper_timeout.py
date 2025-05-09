import pytest
import time
from tasks.task import Task
from tasks.executor import TaskExecutor, TaskExecutionError

def test_timeout_and_retry():
    # sleep beyond timeout
    def sleeper(ctx):
        time.sleep(0.05)
        return {"done": True}

    # no retries, timeout=0.01
    executor = TaskExecutor()
    t = Task(name="slow",
             func=sleeper,
             input_keys=[],
             output_keys=['done'],
             max_retries=0,
             retry_delay_seconds=0,
             timeout=0.01)
    executor.register_task(t)

    with pytest.raises(TaskExecutionError) as ei:
        executor.execute("slow")
    # original exception is FutureTimeoutError
    assert "timeout" in str(ei.value.original_exception).lower()
