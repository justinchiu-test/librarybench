import heapq
import time

def pop_next_task(queue):
    """
    Pop the next task tuple (−priority, counter, task_id) from the heap.
    Returns that tuple or None if empty.
    """
    if not queue:
        return None
    return heapq.heappop(queue)

def push_retry(queue, task, counter_ref):
    """
    Schedule a retry of `task` into the priority `queue` using its own priority,
    updating and returning the new counter.
    """
    # Negative priority for max‐heap behavior
    heapq.heappush(queue, (-task.priority, counter_ref[0], task.id))
    counter_ref[0] += 1
    return counter_ref[0]

def execute_task(task):
    """
    Execute task.func(*args, **kwargs).
    On success, set state to SUCCESS and record result.
    On exception, return the exception.
    """
    try:
        res = task.func(*task.args, **task.kwargs)
        task.state = task.state.SUCCESS
        task.result = res
        return None
    except Exception as exc:
        return exc

def handle_execution(task, retry_policy, queue, counter_ref, TaskState):
    """
    Attempt to execute `task`.  If it raises, retry up to retry_policy.max_retries,
    sleeping retry_policy.retry_delay_seconds between retries, and
    re‐queueing via push_retry.
    On final failure, set state to FAILED and record error.
    """
    try:
        res = task.func(*task.args, **task.kwargs)
        task.state = TaskState.SUCCESS
        task.result = res
    except Exception as exc:
        # can we retry?
        if task.retries_done < retry_policy.max_retries:
            task.retries_done += 1
            time.sleep(retry_policy.retry_delay_seconds)
            # schedule retry
            heapq.heappush(queue, (-task.priority, counter_ref[0], task.id))
            counter_ref[0] += 1
        else:
            task.state = TaskState.FAILED
            task.error = str(exc)
