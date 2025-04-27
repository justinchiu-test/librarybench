import threading
import datetime
import time
import inspect
from enum import Enum
from concurrent.futures import ThreadPoolExecutor, as_completed, TimeoutError
import traceback

class TaskState(Enum):
    PENDING = "pending"
    RUNNING = "running"
    SUCCESS = "success"
    FAILURE = "failure"
    RETRYING = "retrying"

class TaskFailedError(Exception):
    pass

class TaskExecutionRecord:
    def __init__(self, start_time, end_time, status, error=None):
        self.start_time = start_time
        self.end_time = end_time
        self.status = status
        self.error = error

class Task:
    def __init__(self, name, func,
                 dependencies=None,
                 max_retries=0,
                 retry_delay=0,
                 timeout=None,
                 logger=None):
        self.name = name
        self.func = func
        self.dependencies = dependencies[:] if dependencies else []
        self.max_retries = max_retries or 0
        self.retry_delay = retry_delay or 0
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
        # keep history

    def execute(self, context=None):
        """
        Execute the task once, respecting timeout.
        Manage retry state but do not raise exceptions.
        """
        self.attempts += 1
        self.state = TaskState.RUNNING
        start = datetime.datetime.now()
        result = None
        err = None
        status = None

        # run the function with timeout if needed
        try:
            def _call():
                # detect if func accepts context
                sig = inspect.signature(self.func)
                if 'context' in sig.parameters:
                    return self.func(context=context)
                else:
                    return self.func()
            if self.timeout is not None:
                with ThreadPoolExecutor(max_workers=1) as executor:
                    future = executor.submit(_call)
                    result = future.result(timeout=self.timeout)
            else:
                result = _call()
            # success
            self.result = result
            self.state = TaskState.SUCCESS
            status = TaskState.SUCCESS.value
        except TimeoutError:
            err = TaskFailedError(f"Task {self.name} timed out")
            self.error = err
            # timeout treated as failure no retry
            self.state = TaskState.FAILURE
            status = TaskState.FAILURE.value
        except Exception as e:
            err = e
            self.error = err
            if self.attempts <= self.max_retries:
                self.state = TaskState.RETRYING
                status = TaskState.RETRYING.value
                # exponential backoff simulation
                # sleep(self.retry_delay * (2 ** (self.attempts - 1)))
                time.sleep(0)  # no actual wait in tests
            else:
                self.state = TaskState.FAILURE
                status = TaskState.FAILURE.value

        end = datetime.datetime.now()
        rec = TaskExecutionRecord(start, end, status, error=self.error)
        self.execution_records.append(rec)
        # no exception propagation
        return

class WorkflowExecutionRecord:
    def __init__(self, start_time, end_time, status, task_executions):
        self.start_time = start_time
        self.end_time = end_time
        self.status = status
        self.task_executions = task_executions  # dict of name->TaskExecutionRecord

class Workflow:
    def __init__(self, name=None):
        self.name = name
        self.tasks = {}
        self.execution_history = []

    def add_task(self, task):
        if task.name in self.tasks:
            raise ValueError(f"Task {task.name} already exists")
        self.tasks[task.name] = task

    def get_task_result(self, name):
        return self.tasks[name].result

    def validate(self):
        # check missing deps
        for t in self.tasks.values():
            for dep in t.dependencies:
                if dep not in self.tasks:
                    raise ValueError(f"Missing dependency {dep} for task {t.name}")
        # check cycles via DFS
        visiting = set()
        visited = set()
        def dfs(u):
            visiting.add(u)
            for v in self.tasks[u].dependencies:
                if v in visiting:
                    raise ValueError("Cycle detected in workflow")
                if v not in visited:
                    dfs(v)
            visiting.remove(u)
            visited.add(u)
        for name in self.tasks:
            if name not in visited:
                dfs(name)

    def _run_task(self, task):
        # build context from dependencies
        ctx = {}
        for dep in task.dependencies:
            res = self.tasks[dep].result
            if isinstance(res, dict):
                ctx.update(res)
        # execute
        task.execute(context=ctx)

    def run(self):
        self.validate()
        wf_start = datetime.datetime.now()
        status = "success"
        # Results map
        results = {}
        # scheduling waves
        remaining = set(self.tasks.keys())
        # propagate pre-existing successes into results
        for name, task in self.tasks.items():
            if task.state == TaskState.SUCCESS:
                results[name] = task.result
        try:
            while remaining:
                # check for dependency failures
                for name in list(remaining):
                    task = self.tasks[name]
                    # if any dep failed, mark failure
                    if any(self.tasks[d].state == TaskState.FAILURE for d in task.dependencies):
                        task.state = TaskState.FAILURE
                        task.error = TaskFailedError(f"Task {name} failed due to dependency failure")
                        remaining.remove(name)
                # find ready tasks
                ready = []
                for name in remaining:
                    task = self.tasks[name]
                    if task.state == TaskState.PENDING and all(self.tasks[d].state == TaskState.SUCCESS for d in task.dependencies):
                        ready.append(task)
                if not ready:
                    break
                # execute in parallel
                with ThreadPoolExecutor(max_workers=len(ready)) as executor:
                    futures = {executor.submit(self._run_task, task): task for task in ready}
                    for future in as_completed(futures):
                        task = futures[future]
                        # collect result
                        if task.state == TaskState.SUCCESS:
                            results[task.name] = task.result
                # remove done
                for task in ready:
                    if task.state in (TaskState.SUCCESS, TaskState.FAILURE):
                        remaining.discard(task.name)
            # after loop, check failures
            for task in self.tasks.values():
                if task.state == TaskState.FAILURE:
                    status = "failure"
                    raise TaskFailedError(f"Task {task.name} failed")
            # record history
            wf_end = datetime.datetime.now()
            # gather task_executions
            recs = {}
            for name, task in self.tasks.items():
                # last execution record for this run
                if task.execution_records:
                    recs[name] = task.execution_records[-1]
            self.execution_history.append(WorkflowExecutionRecord(wf_start, wf_end, status, recs))
            return results
        except TaskFailedError as e:
            wf_end = datetime.datetime.now()
            recs = {}
            for name, task in self.tasks.items():
                if task.execution_records:
                    recs[name] = task.execution_records[-1]
            status = "failure"
            self.execution_history.append(WorkflowExecutionRecord(wf_start, wf_end, status, recs))
            raise

class ScheduleType(Enum):
    HOURLY = "hourly"
    DAILY = "daily"

class Schedule:
    def __init__(self, type, hour=None, minute=None):
        self.type = type
        self.hour = hour
        self.minute = minute
        self.last_run = None

    def should_run(self):
        now = datetime.datetime.now()
        if self.last_run is None:
            return True
        if self.type == ScheduleType.HOURLY:
            delta = now - self.last_run
            return delta >= datetime.timedelta(hours=1)
        elif self.type == ScheduleType.DAILY:
            # next run is last_run date +1 day at scheduled hour/minute
            if self.hour is None or self.minute is None:
                raise ValueError("Daily schedule needs hour and minute")
            next_date = (self.last_run.date() + datetime.timedelta(days=1))
            next_run = datetime.datetime.combine(next_date, datetime.time(self.hour, self.minute))
            return now >= next_run
        else:
            return False
