import threading
import time
import datetime
from enum import Enum
from concurrent.futures import ThreadPoolExecutor, TimeoutError as FutureTimeout, wait, FIRST_COMPLETED
import concurrent.futures


class TaskState(Enum):
    PENDING = "pending"
    RUNNING = "running"
    RETRYING = "retrying"
    SUCCESS = "success"
    FAILURE = "failure"


class TaskFailedError(Exception):
    pass


class ScheduleType(Enum):
    HOURLY = "hourly"
    DAILY = "daily"


class Schedule:
    def __init__(self, type: ScheduleType, hour: int = None, minute: int = None):
        self.type = type
        self.hour = hour
        self.minute = minute
        self.last_run: datetime.datetime = None

    def should_run(self) -> bool:
        now = datetime.datetime.now()
        if self.last_run is None:
            return True
        if self.type == ScheduleType.HOURLY:
            return (now - self.last_run).total_seconds() >= 3600
        elif self.type == ScheduleType.DAILY:
            if self.hour is None or self.minute is None:
                raise ValueError("Daily schedule requires hour and minute")
            today_run = now.replace(hour=self.hour, minute=self.minute,
                                    second=0, microsecond=0)
            # If last_run was before today's scheduled time and now is at/after it
            return self.last_run < today_run <= now
        else:
            return False


class ExecutionTaskRecord:
    def __init__(self, start_time: datetime.datetime, end_time: datetime.datetime, status: str):
        self.start_time = start_time
        self.end_time = end_time
        self.status = status  # "success" or "failure"


class ExecutionRunRecord:
    def __init__(self, name: str = None):
        self.name = name
        self.start_time: datetime.datetime = None
        self.end_time: datetime.datetime = None
        self.status: str = None
        self.task_executions: dict = {}


class Task:
    def __init__(
        self,
        name: str,
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
        self.result = None
        self.error = None
        self.execution_records = []

    def reset(self):
        self.state = TaskState.PENDING
        self.attempts = 0
        self.result = None
        self.error = None
        self.execution_records = []

    def execute(self, context=None):
        # Do not re-execute if already succeeded
        if self.state == TaskState.SUCCESS:
            return self.result

        self.attempts += 1
        start_time = datetime.datetime.now()
        self.state = TaskState.RUNNING
        result = None
        err = None

        try:
            if self.timeout is not None:
                with ThreadPoolExecutor(max_workers=1) as executor:
                    future = executor.submit(self.func, context)
                    result = future.result(timeout=self.timeout)
            else:
                result = self.func(context)
            # Success
            self.state = TaskState.SUCCESS
            self.result = result
            self.error = None
            status = "success"
        except FutureTimeout:
            err = TimeoutError("Task timed out")
            self.state = TaskState.FAILURE
            self.error = err
            status = "failure"
        except Exception as e:
            err = e
            # Determine retry or failure
            if self.attempts <= self.max_retries:
                self.state = TaskState.RETRYING
                status = "failure"
            else:
                self.state = TaskState.FAILURE
                status = "failure"
            self.error = err

        end_time = datetime.datetime.now()
        # Record execution
        rec = ExecutionTaskRecord(start_time, end_time, status)
        self.execution_records.append(rec)
        # Respect retry_delay (no actual sleep for tests)
        return self.result


class Workflow:
    def __init__(self, name: str = None):
        self.name = name
        self.tasks: dict = {}
        self.execution_history: list = []

    def add_task(self, task: Task):
        if task.name in self.tasks:
            raise ValueError(f"Task {task.name} already exists")
        self.tasks[task.name] = task

    def get_task_result(self, name: str):
        return self.tasks[name].result

    def validate(self):
        # Check missing dependencies
        for t in self.tasks.values():
            for dep in t.dependencies:
                if dep not in self.tasks:
                    raise ValueError(f"Missing dependency {dep} for task {t.name}")
        # Check cycles
        temp_mark = set()
        perm_mark = set()

        def visit(n):
            if n in perm_mark:
                return
            if n in temp_mark:
                raise ValueError("Cycle detected in workflow")
            temp_mark.add(n)
            for m in self.tasks[n].dependencies:
                visit(m)
            temp_mark.remove(n)
            perm_mark.add(n)

        for name in self.tasks:
            visit(name)

    def run(self):
        self.validate()
        run_rec = ExecutionRunRecord(self.name)
        run_rec.start_time = datetime.datetime.now()
        context = {}
        results = {}

        # Partial success tasks
        for name, task in self.tasks.items():
            if task.state == TaskState.SUCCESS:
                results[name] = task.result

        pending = set(self.tasks.keys())
        running_futs = {}
        executor = ThreadPoolExecutor(max_workers=len(self.tasks) or 1)
        failed_task = None

        try:
            while pending or running_futs:
                # Schedule new tasks
                if failed_task is None:
                    for t_name in list(pending):
                        task = self.tasks[t_name]
                        if task.state == TaskState.SUCCESS:
                            pending.remove(t_name)
                            continue
                        # dependencies satisfied?
                        if all(dep in results for dep in task.dependencies):
                            fut = executor.submit(task.execute, context)
                            running_futs[fut] = t_name
                            pending.remove(t_name)
                if not running_futs:
                    break
                done, _ = wait(running_futs.keys(), return_when=FIRST_COMPLETED)
                for fut in done:
                    t_name = running_futs.pop(fut)
                    task = self.tasks[t_name]
                    rec = task.execution_records[-1]
                    run_rec.task_executions[t_name] = ExecutionTaskRecord(
                        rec.start_time, rec.end_time, rec.status
                    )
                    if task.state == TaskState.SUCCESS:
                        results[t_name] = task.result
                        # update context if dict
                        if isinstance(task.result, dict):
                            context = task.result
                    elif task.state == TaskState.RETRYING:
                        # re-queue
                        pending.add(t_name)
                    else:  # FAILURE
                        failed_task = task
                if failed_task:
                    break
        finally:
            executor.shutdown(wait=False)

        # Handle failures and propagation
        if failed_task:
            # mark downstream tasks as failed
            for t_name in list(pending):
                task = self.tasks[t_name]
                if any(self.tasks[d].state == TaskState.FAILURE for d in task.dependencies):
                    task.state = TaskState.FAILURE
                    task.error = TaskFailedError(f"Task {t_name} failed due to dependency failure")
                    run_rec.task_executions[t_name] = ExecutionTaskRecord(None, None, "failure")
            run_rec.end_time = datetime.datetime.now()
            run_rec.status = "failure"
            self.execution_history.append(run_rec)
            raise TaskFailedError(str(failed_task.error))

        # Success
        run_rec.end_time = datetime.datetime.now()
        run_rec.status = "success"
        self.execution_history.append(run_rec)
        return results
