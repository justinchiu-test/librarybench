import time
from concurrent.futures import ThreadPoolExecutor, TimeoutError as FuturesTimeoutError

class Task:
    def __init__(self, name, func, max_retries=0, backoff_factor=1, timeout_seconds=None):
        """
        name: unique task name
        func: callable taking a TaskContext
        max_retries: number of retries on failure (default 0)
        backoff_factor: base backoff multiplier (default 1)
        timeout_seconds: if set, timeout per attempt in seconds
        """
        self.name = name
        self.func = func
        self.max_retries = max_retries
        self.backoff_factor = backoff_factor
        self.timeout_seconds = timeout_seconds

class TaskContext:
    def __init__(self, runner, task):
        self._runner = runner
        self._task = task
        self._storage = runner.shared_storage

    def set(self, key, value):
        """Set a key/value in shared context storage."""
        self._storage[key] = value

    def get(self, key, default=None):
        """Get a value from shared context storage."""
        return self._storage.get(key, default)

    def add_task(self, task):
        """Dynamically add a task to the runner."""
        self._runner.add_task(task)

class TaskRunner:
    def __init__(self, sleep_fn=None):
        """
        sleep_fn: function(seconds) to sleep, default time.sleep
        """
        self.sleep_fn = sleep_fn if sleep_fn is not None else time.sleep
        self.shared_storage = {}
        self.outputs = {}
        self.exceptions = {}
        # internal queue of tasks (allows dynamic addition)
        self._tasks = []

    def add_task(self, task):
        """Register a Task for execution."""
        self._tasks.append(task)

    def run(self):
        """
        Execute all registered tasks, including those added dynamically.
        Returns a dict of task_name -> result.
        Raises the first exception encountered when retries are exhausted.
        """
        # reset outputs/exceptions
        self.outputs = {}
        self.exceptions = {}
        # use index-based iteration to allow dynamic additions
        idx = 0
        while idx < len(self._tasks):
            task = self._tasks[idx]
            idx += 1
            attempt = 0
            while True:
                ctx = TaskContext(self, task)
                try:
                    # handle possible timeout
                    if task.timeout_seconds is not None:
                        with ThreadPoolExecutor(max_workers=1) as executor:
                            future = executor.submit(task.func, ctx)
                            result = future.result(timeout=task.timeout_seconds)
                    else:
                        result = task.func(ctx)
                    # on success, record output
                    self.outputs[task.name] = result
                    # also expose under "output:<task_name>"
                    self.shared_storage[f"output:{task.name}"] = result
                    break
                except Exception as e:
                    # normalize timeout from futures
                    if isinstance(e, FuturesTimeoutError):
                        err = TimeoutError(f"Task {task.name} timed out after {task.timeout_seconds} seconds")
                    else:
                        err = e
                    # check retry allowance
                    if attempt < task.max_retries:
                        # sleep with backoff if configured
                        attempt += 1
                        bf = getattr(task, "backoff_factor", 1) or 0
                        if bf > 0:
                            delay = bf * (2 ** (attempt - 1))
                            self.sleep_fn(delay)
                        # retry
                        continue
                    # no more retries: record and propagate
                    self.exceptions[task.name] = err
                    raise err
        return self.outputs
