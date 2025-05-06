import time
from .models import TaskState

def execute_task(task):
    """
    Execute a Task and update its state according to its retry_policy.
    On success, sets state=SUCCESS and task.result.
    On exception, increments retries_done, and either sets state=PENDING
    (for retry) or state=FAILURE.
    """
    try:
        res = task.func(*task.args, **task.kwargs)
    except Exception:
        task.retries_done += 1
        # safe‐guard in case retry_policy is None
        rp = task.retry_policy or type('RP', (), {'max_retries': 0, 'retry_delay_seconds': 0.0})()
        if task.retries_done <= rp.max_retries:
            time.sleep(rp.retry_delay_seconds)
            task.state = TaskState.PENDING
        else:
            task.state = TaskState.FAILURE
    else:
        task.state = TaskState.SUCCESS
        task.result = res
