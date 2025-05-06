import time
from concurrent.futures import ThreadPoolExecutor, TimeoutError
from .core import TaskState, TaskMetadata, TaskContext
from .exceptions import TaskTimeoutError, TaskExecutionError
from .retry import get_backoff_delay

class Task:
    def __init__(self, name, func, inputs=None,
                 max_retries=0, retry_delay_seconds=0.0,
                 timeout_seconds=None, backoff=True):
        self.name = name
        self.func = func
        self.inputs = inputs or {}
        self.max_retries = max_retries
        self.retry_delay_seconds = retry_delay_seconds
        self.timeout_seconds = timeout_seconds
        self.backoff = backoff

class TaskManager:
    def __init__(self, alert_service=None):
        self.tasks = []
        self.context = TaskContext()
        self.metadata = {}
        self.alert_service = alert_service

    def add_task(self, task):
        self.tasks.append(task)

    def run_all(self):
        results = {}
        idx = 0
        while idx < len(self.tasks):
            t = self.tasks[idx]; idx += 1
            meta = TaskMetadata(t.name)
            self.metadata[t.name] = meta
            meta.start_time = time.time()
            meta.status = TaskState.RUNNING

            total = t.max_retries + 1
            last_err = None
            out = None

            for attempt in range(1, total + 1):
                meta.attempts = attempt
                try:
                    self.context.set("manager", self)
                    with ThreadPoolExecutor(max_workers=1) as ex:
                        fut = ex.submit(t.func, self.context, t.inputs)
                        out = fut.result(timeout=t.timeout_seconds)
                    meta.status = TaskState.SUCCESS
                    last_err = None
                    break
                except TimeoutError:
                    last_err = TaskTimeoutError(
                        f"Task '{t.name}' timed out after {t.timeout_seconds}s"
                    )
                except Exception as e:
                    last_err = TaskExecutionError(f"Task '{t.name}' failed: {e}")

                if attempt < total:
                    delay = t.retry_delay_seconds
                    if t.backoff:
                        delay = get_backoff_delay(attempt, t.retry_delay_seconds)
                    time.sleep(delay)
                else:
                    meta.status = TaskState.FAILURE

            meta.end_time = time.time()
            meta.error = last_err

            if isinstance(out, dict):
                for k, v in out.items():
                    self.context.set(k, v)
                results[t.name] = out

            if self.alert_service:
                msg = (f"Task '{t.name}' failed after {meta.attempts} attempt(s): {meta.error}"
                       if meta.status == TaskState.FAILURE
                       else f"Task '{t.name}' succeeded in {meta.attempts} attempt(s)")
                self.alert_service.send_alert(msg)

        return results
