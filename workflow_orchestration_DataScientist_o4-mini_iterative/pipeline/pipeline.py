import time
from concurrent.futures import ThreadPoolExecutor, TimeoutError
from .exceptions import TaskTimeout
from .task import Task

class Pipeline:
    """
    Orchestrates execution of a set of tasks.
    Respects input-based dependencies, handles retries, backoff, timeouts, dynamic tasks,
    records metadata, and sends alerts on failure.
    """
    def __init__(self, tasks, context, metadata_storage, notifier):
        # tasks: list of Task instances
        self.tasks = {t.name: t for t in tasks}
        self.context = context
        self.metadata = metadata_storage
        self.notifier = notifier

    def run(self):
        pending = set(self.tasks.keys())
        while pending:
            # find tasks whose inputs are all in context
            runnable = [
                name for name in pending
                if all(self.context.get(k) is not None for k in self.tasks[name].inputs)
            ]
            if not runnable:
                raise Exception("No runnable tasks found; possible unmet dependencies or circularity")
            for name in runnable:
                task = self.tasks[name]
                self._run_task(task)
                pending.remove(name)

    def _run_task(self, task):
        task.state = 'running'
        attempt = 0
        last_exc = None
        metadata = {
            'start_time': time.time(),
            'end_time': None,
            'status': None,
            'attempts': 0
        }
        while attempt <= task.max_retries:
            attempt += 1
            metadata['attempts'] = attempt
            try:
                result = self._execute_with_timeout(task)
                # success
                task.state = 'success'
                metadata['status'] = 'success'
                metadata['end_time'] = time.time()
                self.metadata.record(task.name, metadata.copy())
                # handle outputs
                if isinstance(result, dict):
                    for k, v in result.items():
                        self.context.set(k, v)
                # handle dynamic tasks
                if isinstance(result, list):
                    for new_task in result:
                        if new_task.name in self.tasks:
                            continue
                        self.tasks[new_task.name] = new_task
                return
            except TaskTimeout as e:
                last_exc = e
                if attempt > task.max_retries:
                    break
                delay = self._compute_delay(task, attempt)
                time.sleep(delay)
            except Exception as e:
                last_exc = e
                if attempt > task.max_retries:
                    break
                delay = self._compute_delay(task, attempt)
                time.sleep(delay)
        # if we get here, task failed after retries
        task.state = 'failure'
        metadata['status'] = 'failure'
        metadata['end_time'] = time.time()
        self.metadata.record(task.name, metadata.copy())
        # send alert
        self.notifier.send(
            f"Task {task.name} failed after {attempt} attempts. Exception: {last_exc}"
        )

    def _execute_with_timeout(self, task):
        if task.timeout is not None:
            with ThreadPoolExecutor(max_workers=1) as executor:
                future = executor.submit(task.func, self.context)
                try:
                    return future.result(timeout=task.timeout)
                except TimeoutError:
                    raise TaskTimeout(f"Task {task.name} timed out after {task.timeout} seconds")
        else:
            return task.func(self.context)

    def _compute_delay(self, task, attempt):
        base = task.retry_delay_seconds
        if task.backoff:
            return base * (2 ** (attempt - 1))
        return base
