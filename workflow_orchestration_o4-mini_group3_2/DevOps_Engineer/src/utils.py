import time
import traceback
from collections import defaultdict, deque
from concurrent.futures import ThreadPoolExecutor, TimeoutError

def execute_with_retries(func, timeout, max_retries, retry_delay_seconds,
                         logger, task_name):
    """
    Execute func with a ThreadPoolExecutor, enforcing timeout and retry with
    exponential backoff. Returns a tuple:
      (status_str, attempts, start_time, end_time, last_exception)
    """
    attempts = 0
    last_exception = None
    start_time = None
    end_time = None
    status = "FAILED"
    while attempts <= max_retries:
        attempts += 1
        start_time = time.time()
        logger.info(f"Task {task_name} attempt {attempts} started.")
        with ThreadPoolExecutor(max_workers=1) as executor:
            future = executor.submit(func)
            try:
                future.result(timeout=timeout)
                status = "SUCCESS"
                logger.info(f"Task {task_name} succeeded.")
                last_exception = None
                break
            except TimeoutError:
                status = "FAILED"
                last_exception = TimeoutError(f"Task {task_name} timed out.")
                logger.error(f"Task {task_name} timed out on attempt {attempts}.")
            except Exception as e:
                status = "FAILED"
                last_exception = e
                tb = traceback.format_exc()
                logger.error(f"Task {task_name} failed on attempt {attempts}: {tb}")
        end_time = time.time()
        if status == "SUCCESS":
            break
        if attempts <= max_retries:
            backoff = retry_delay_seconds * (2 ** (attempts - 1))
            logger.info(f"Task {task_name} retrying after {backoff} seconds backoff.")
            time.sleep(backoff)
    end_time = end_time or time.time()
    return status, attempts, start_time, end_time, last_exception

def topological_sort(tasks):
    """
    Given a dict of name->task with .dependencies (iterable of names),
    return a list of names in topological order; raises ValueError on cycles.
    """
    indegree = defaultdict(int)
    graph = defaultdict(list)
    for name, task in tasks.items():
        indegree[name]  # ensure key exists
        for dep in task.dependencies:
            graph[dep].append(name)
            indegree[name] += 1
    queue = deque([n for n, d in indegree.items() if d == 0])
    order = []
    while queue:
        u = queue.popleft()
        order.append(u)
        for v in graph[u]:
            indegree[v] -= 1
            if indegree[v] == 0:
                queue.append(v)
    if len(order) != len(tasks):
        raise ValueError("Cycle detected in task dependencies")
    return order
