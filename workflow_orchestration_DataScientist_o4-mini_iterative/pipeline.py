import time
from collections import deque
from concurrent.futures import ThreadPoolExecutor, TimeoutError as FuturesTimeoutError


class ExecutionContext:
    def __init__(self):
        self._store = {}

    def set(self, key, value):
        self._store[key] = value

    def get(self, key):
        return self._store.get(key)


class MetadataStorage:
    def __init__(self):
        self._data = {}

    def add(self, task_name, record):
        self._data.setdefault(task_name, []).append(record)

    def get_all(self, task_name):
        return self._data.get(task_name, [])


class DummyNotifier:
    def __init__(self):
        self.alerts = []

    def notify(self, message):
        # message can be an Exception; store it for inspection
        self.alerts.append(message)


class Task:
    def __init__(
        self,
        name,
        func,
        inputs=None,
        outputs=None,
        max_retries=0,
        retry_delay_seconds=0,
        backoff=False,
        timeout=None,
    ):
        self.name = name
        self.func = func
        self.inputs = inputs or []
        self.outputs = outputs or []
        self.max_retries = max_retries
        self.retry_delay_seconds = retry_delay_seconds
        self.backoff = backoff
        self.timeout = timeout

        # These are mutated by the runner:
        self.state = None        # "success" or "failure"
        self.attempts = 0        # how many times we actually ran the func


class Pipeline:
    def __init__(self, tasks, context, metadata, notifier):
        self.tasks = list(tasks)
        self.context = context
        self.metadata = metadata
        self.notifier = notifier

    def run(self):
        queue = deque(self.tasks)

        while queue:
            task = queue.popleft()

            # 1) Check that required inputs are already in the context
            missing = [inp for inp in task.inputs if self.context.get(inp) is None]
            if missing:
                task.state = "failure"
                # No retries on missing inputs
                self.metadata.add(task.name, {"state": task.state, "attempts": task.attempts})
                continue

            # 2) Try to execute (with retries/timeouts)
            try:
                result = self._execute_with_retries(task)
            except Exception as exc:
                # Final failure
                task.state = "failure"
                self.notifier.notify(exc)
                self.metadata.add(task.name, {"state": task.state, "attempts": task.attempts})
                continue

            # 3) On success, record outputs or enqueue dynamic tasks
            if isinstance(result, list):
                # creator task returned new Task instances
                task.state = "success"
                self.metadata.add(task.name, {"state": task.state, "attempts": task.attempts})
                for new_task in result:
                    queue.append(new_task)
            else:
                # normal dict of outputs
                for k, v in result.items():
                    self.context.set(k, v)
                task.state = "success"
                self.metadata.add(task.name, {"state": task.state, "attempts": task.attempts})

    def _execute_with_retries(self, task):
        delay = task.retry_delay_seconds

        while True:
            task.attempts += 1
            try:
                if task.timeout is not None:
                    # run with timeout
                    with ThreadPoolExecutor(max_workers=1) as executor:
                        future = executor.submit(task.func, self.context)
                        result = future.result(timeout=task.timeout)
                else:
                    result = task.func(self.context)
                return result

            except FuturesTimeoutError:
                # treat as a TimeoutError
                exc = TimeoutError(f"Task '{task.name}' timed out after {task.timeout}s")
            except Exception as e:
                exc = e

            # If no retries remain, re‐raise
            if task.attempts > task.max_retries:
                raise exc

            # Otherwise wait and possibly back off, then retry
            time.sleep(delay)
            if task.backoff:
                delay *= 2
