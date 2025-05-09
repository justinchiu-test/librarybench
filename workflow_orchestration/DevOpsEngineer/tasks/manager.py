import time
from concurrent.futures import ThreadPoolExecutor, TimeoutError
from .core import TaskState, TaskMetadata, TaskContext
from .exceptions import TaskTimeoutError, TaskExecutionError
from .retry import get_backoff_delay

class Task:
    """
    Represents a unit of work.
    func: a callable(context: TaskContext, inputs: dict) -> dict (outputs)
    """
    def __init__(
        self,
        name,
        func,
        inputs=None,
        max_retries=0,
        retry_delay_seconds=0.0,
        timeout_seconds=None,
        backoff=True
    ):
        self.name = name
        self.func = func
        self.inputs = inputs or {}
        self.max_retries = max_retries
        self.retry_delay_seconds = retry_delay_seconds
        self.timeout_seconds = timeout_seconds
        self.backoff = backoff

class TaskManager:
    """
    Manages registration and execution of tasks with retry, timeout, alerting, and metadata.
    """
    def __init__(self, alert_service=None):
        self.tasks = []
        self.context = TaskContext()
        self.metadata = {}  # name -> TaskMetadata
        self.alert_service = alert_service

    def add_task(self, task: Task):
        """Register a new task (can be called dynamically during execution)."""
        self.tasks.append(task)

    def run_all(self):
        """
        Executes all registered tasks in sequence.
        Returns a dict of task name -> outputs dict.
        """
        results = {}
        # We snapshot the list so dynamic additions in this run will also execute
        idx = 0
        while idx < len(self.tasks):
            task = self.tasks[idx]
            idx += 1

            # Prepare metadata
            meta = TaskMetadata(task.name)
            self.metadata[task.name] = meta
            meta.start_time = time.time()
            meta.status = TaskState.RUNNING

            total_attempts = task.max_retries + 1
            last_error = None
            outputs = None

            for attempt in range(1, total_attempts + 1):
                meta.attempts = attempt
                try:
                    # Inject manager into context for dynamic task creation
                    self.context.set("manager", self)
                    with ThreadPoolExecutor(max_workers=1) as executor:
                        future = executor.submit(task.func, self.context, task.inputs)
                        outputs = future.result(timeout=task.timeout_seconds)
                    meta.status = TaskState.SUCCESS
                    last_error = None
                    break
                except TimeoutError:
                    last_error = TaskTimeoutError(
                        f"Task '{task.name}' timed out after {task.timeout_seconds}s"
                    )
                except Exception as e:
                    last_error = TaskExecutionError(f"Task '{task.name}' failed: {e}")

                # If we can retry, wait then loop
                if attempt < total_attempts:
                    delay = task.retry_delay_seconds
                    if task.backoff:
                        delay = get_backoff_delay(attempt, task.retry_delay_seconds)
                    time.sleep(delay)
                else:
                    meta.status = TaskState.FAILURE

            meta.end_time = time.time()
            meta.error = last_error

            # Merge outputs into context and results on success
            if outputs and isinstance(outputs, dict):
                for k, v in outputs.items():
                    self.context.set(k, v)
                results[task.name] = outputs

            # Send alerts
            if self.alert_service:
                if meta.status == TaskState.FAILURE:
                    self.alert_service.send_alert(
                        f"Task '{task.name}' failed after {meta.attempts} attempt(s): {meta.error}"
                    )
                else:
                    self.alert_service.send_alert(
                        f"Task '{task.name}' succeeded in {meta.attempts} attempt(s)"
                    )

        return results
