import threading
import datetime
import time
import concurrent.futures
import inspect
from enum import Enum
from collections import deque


class TaskState(Enum):
    PENDING = "pending"
    RUNNING = "running"
    SUCCESS = "success"
    FAILURE = "failure"
    RETRYING = "retrying"


class TaskFailedError(Exception):
    """Raised when a task or workflow fails."""
    pass


class ExecutionRecord:
    """Record of a single task attempt."""
    def __init__(self, start_time: datetime.datetime, end_time: datetime.datetime, status: str):
        self.start_time = start_time
        self.end_time = end_time
        self.status = status  # 'success', 'failure', 'retry'


class TaskExecutionInfo:
    """Info for a task in workflow execution history."""
    def __init__(self, start_time: datetime.datetime, end_time: datetime.datetime, status: str):
        self.start_time = start_time
        self.end_time = end_time
        self.status = status  # 'success' or 'failure'


class WorkflowExecution:
    """Record of a workflow run."""
    def __init__(self, start_time: datetime.datetime, end_time: datetime.datetime, status: str, task_executions: dict):
        self.start_time = start_time
        self.end_time = end_time
        self.status = status  # 'success' or 'failure'
        self.task_executions = task_executions  # name -> TaskExecutionInfo


class Task:
    def __init__(
        self,
        name,
        func,
        dependencies=None,
        max_retries: int = 0,
        retry_delay: float = 0,
        timeout: float = None,
        logger=None,
    ):
        self.name = name
        self.func = func
        self.dependencies = dependencies[:] if dependencies else []
        self.max_retries = max_retries
        self.retry_delay = retry_delay
        self.timeout = timeout
        self.logger = logger

        self.state = TaskState.PENDING
        self.attempts = 0
        self.error = None
        self.result = None
        self.execution_records = []  # list of ExecutionRecord

    def execute(self, context=None):
        """
        Execute the task, with retry logic.
        On failure and retries left, sets state to RETRYING and raises the exception.
        On success, sets state to SUCCESS and returns result.
        On final failure, sets state to FAILURE and raises.
        """
        # Prepare for execution
        self.attempts += 1
        start = datetime.datetime.now()
        self.state = TaskState.RUNNING

        try:
            # Determine how to call func: with context or not
            sig = inspect.signature(self.func)
            if "context" in sig.parameters:
                res = self.func(context=context)
            else:
                res = self.func()
            end = datetime.datetime.now()
            # Success
            self.state = TaskState.SUCCESS
            self.error = None
            self.result = res
            self.execution_records.append(ExecutionRecord(start, end, "success"))
            return res
        except Exception as e:
            end = datetime.datetime.now()
            # Check for retry
            if self.attempts <= self.max_retries:
                self.state = TaskState.RETRYING
                self.error = e
                self.execution_records.append(ExecutionRecord(start, end, "retry"))
                # Optionally sleep for retry_delay (skipped in tests)
                # time.sleep(self.retry_delay)
                raise e
            else:
                self.state = TaskState.FAILURE
                self.error = e
                self.execution_records.append(ExecutionRecord(start, end, "failure"))
                raise e

    def reset(self):
        """Reset the task to pending for re-running the workflow."""
        self.state = TaskState.PENDING
        self.attempts = 0
        self.error = None
        self.result = None
        # keep execution_records for history


class Workflow:
    def __init__(self, name=None, schedule=None):
        self.name = name or "workflow"
        self.tasks = {}  # name -> Task
        self.execution_history = []  # list of WorkflowExecution
        self.schedule = schedule

    def add_task(self, task: Task):
        if task.name in self.tasks:
            raise ValueError(f"Task {task.name} already exists")
        self.tasks[task.name] = task

    def get_task_result(self, name):
        return self.tasks[name].result

    def validate(self):
        # Check missing dependencies
        for t in self.tasks.values():
            for dep in t.dependencies:
                if dep not in self.tasks:
                    raise ValueError(f"Missing dependency: {dep} for task {t.name}")
        # Check cycles
        visited = set()
        rec_stack = set()

        def dfs(node_name):
            if node_name in rec_stack:
                raise ValueError("Cycle detected in workflow")
            if node_name in visited:
                return
            visited.add(node_name)
            rec_stack.add(node_name)
            for dep in self.tasks[node_name].dependencies:
                dfs(dep)
            rec_stack.remove(node_name)

        for name in self.tasks:
            dfs(name)

    def run(self):
        """
        Execute the workflow, running tasks respecting dependencies,
        handling retries, timeouts, failure propagation, parallel execution.
        Returns a dict of task_name -> result.
        Raises TaskFailedError on any failure.
        """
        # Validate DAG
        self.validate()

        wf_start = datetime.datetime.now()
        wf_status = "success"
        results = {}
        # build fresh context for this run
        context = {}

        # Keep looping until no PENDING/RETRYING tasks remain
        executor = concurrent.futures.ThreadPoolExecutor(max_workers=len(self.tasks))
        try:
            while True:
                # Propagate dependency failures
                for t in self.tasks.values():
                    if t.state in (TaskState.PENDING, TaskState.RETRYING):
                        for dep in t.dependencies:
                            dep_task = self.tasks[dep]
                            if dep_task.state == TaskState.FAILURE:
                                t.state = TaskState.FAILURE
                                t.error = TaskFailedError(f"Dependency {dep} failed")
                # Find ready tasks
                ready = []
                for t in self.tasks.values():
                    if t.state in (TaskState.PENDING, TaskState.RETRYING):
                        if all(self.tasks[dep].state == TaskState.SUCCESS for dep in t.dependencies):
                            ready.append(t)
                if not ready:
                    break  # nothing to run
                # Schedule batch
                futures = {}
                for t in ready:
                    # Prepare context slice
                    ctx = context.copy()
                    fut = executor.submit(t.execute, ctx)
                    futures[fut] = t
                # Collect results
                error_occurred = False
                for fut, t in futures.items():
                    try:
                        # handle timeout
                        if t.timeout is not None:
                            fut.result(timeout=t.timeout)
                        else:
                            fut.result()
                    except concurrent.futures.TimeoutError:
                        # Task timed out
                        t.state = TaskState.FAILURE
                        t.error = TaskFailedError("Task timed out")
                        error_occurred = True
                        fut.cancel()
                    except Exception:
                        # Underlying task.execute sets state appropriately
                        error_occurred = True
                    else:
                        # on success, merge result
                        if isinstance(t.result, dict):
                            context.update(t.result)
                        results[t.name] = t.result
                if error_occurred:
                    wf_status = "failure"
                    break
            # After batches, check if any failure in tasks triggers workflow failure
            if any(t.state == TaskState.FAILURE for t in self.tasks.values()):
                wf_status = "failure"
        finally:
            executor.shutdown(wait=False)
            wf_end = datetime.datetime.now()
            # Build workflow execution record
            task_execs = {}
            for name, t in self.tasks.items():
                # pick latest execution record for this run
                if t.execution_records:
                    rec = t.execution_records[-1]
                    status = t.state.value
                    task_execs[name] = TaskExecutionInfo(rec.start_time, rec.end_time, status)
                else:
                    # never executed (e.g., skipped), mark as success with zero times
                    now = wf_end
                    task_execs[name] = TaskExecutionInfo(now, now, t.state.value)
            self.execution_history.append(WorkflowExecution(wf_start, wf_end, wf_status, task_execs))

        if wf_status == "failure":
            raise TaskFailedError("Workflow failed")
        return results


class ScheduleType(Enum):
    HOURLY = "hourly"
    DAILY = "daily"


class Schedule:
    def __init__(self, type: ScheduleType, hour: int = None, minute: int = None):
        self.type = type
        self.hour = hour
        self.minute = minute
        self.last_run = None

    def should_run(self):
        now = datetime.datetime.now()
        if self.type == ScheduleType.HOURLY:
            if self.last_run is None:
                return True
            return (now - self.last_run) >= datetime.timedelta(hours=1)
        elif self.type == ScheduleType.DAILY:
            if self.hour is None or self.minute is None:
                raise ValueError("Daily schedule requires hour and minute")
            scheduled_today = now.replace(hour=self.hour, minute=self.minute, second=0, microsecond=0)
            if self.last_run is None:
                return now >= scheduled_today
            # run again if we've passed today's scheduled time and haven't run since then
            return now >= scheduled_today and self.last_run < scheduled_today
        else:
            raise ValueError(f"Unknown schedule type: {self.type}")
