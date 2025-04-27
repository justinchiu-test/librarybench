import time
import datetime
import threading
import logging
import inspect
from enum import Enum
from concurrent.futures import ThreadPoolExecutor, TimeoutError, as_completed


class TaskState(Enum):
    PENDING = "pending"
    RUNNING = "running"
    SUCCESS = "success"
    FAILURE = "failure"
    RETRYING = "retrying"


class TaskFailedError(Exception):
    pass


class ExecutionRecord:
    def __init__(self, start_time, end_time, status):
        self.start_time = start_time
        self.end_time = end_time
        self.status = status


class WorkflowExecution:
    def __init__(self, start_time, end_time, status, task_executions):
        self.start_time = start_time
        self.end_time = end_time
        self.status = status
        self.task_executions = task_executions  # dict task_name -> ExecutionRecord


class Task:
    def __init__(
        self,
        name,
        func,
        dependencies=None,
        max_retries=0,
        retry_delay=0,
        timeout=None,
        logger=None,
    ):
        self.name = name
        self.func = func
        self.dependencies = dependencies[:] if dependencies else []
        self.max_retries = max_retries
        self.retry_delay = retry_delay
        self.timeout = timeout
        self.logger = logger or logging.getLogger(__name__)

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
        # One attempt
        self.attempts += 1
        self.state = TaskState.RUNNING
        start = datetime.datetime.now()

        def _run_fn():
            # call func with or without context
            sig = inspect.signature(self.func)
            if len(sig.parameters) == 0:
                return self.func()
            else:
                return self.func(context=context)

        try:
            if self.timeout is not None:
                with ThreadPoolExecutor(max_workers=1) as exe:
                    fut = exe.submit(_run_fn)
                    res = fut.result(timeout=self.timeout)
            else:
                res = _run_fn()
            self.result = res
            self.error = None
            self.state = TaskState.SUCCESS
            end = datetime.datetime.now()
            rec = ExecutionRecord(start, end, "success")
            self.execution_records.append(rec)
        except TimeoutError:
            # Task timed out
            end = datetime.datetime.now()
            self.error = Exception("Task timed out")
            self.state = TaskState.FAILURE
            rec = ExecutionRecord(start, end, "failure")
            self.execution_records.append(rec)
        except Exception as e:
            end = datetime.datetime.now()
            self.error = e
            if self.attempts <= self.max_retries:
                self.state = TaskState.RETRYING
            else:
                self.state = TaskState.FAILURE
            rec = ExecutionRecord(start, end, "failure")
            self.execution_records.append(rec)
        return

        
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
            diff = now - self.last_run
            return diff >= datetime.timedelta(hours=1)
        if self.type == ScheduleType.DAILY:
            # require that last_run was before today's scheduled time
            # assume hour and minute are set
            target_today = now.replace(hour=self.hour, minute=self.minute,
                                       second=0, microsecond=0)
            # if last_run < target_today <= now, it's time
            return now >= target_today and self.last_run < target_today
        return False


class Workflow:
    def __init__(self, name=None, schedule=None):
        self.name = name or ""
        self.tasks = {}
        self.execution_history = []
        self.schedule = schedule

    def add_task(self, task):
        if task.name in self.tasks:
            raise ValueError(f"Task {task.name} already exists")
        self.tasks[task.name] = task

    def get_task_result(self, name):
        return self.tasks[name].result

    def validate(self):
        # missing dependencies
        for t in self.tasks.values():
            for dep in t.dependencies:
                if dep not in self.tasks:
                    raise ValueError(f"Missing dependency {dep}")
        # cycle detection
        visited = {}
        def dfs(node):
            if visited.get(node) == 1:
                # currently visiting -> cycle
                raise ValueError("Cycle detected in workflow")
            if visited.get(node) == 2:
                return
            visited[node] = 1
            for nbr in self.tasks[node].dependencies:
                dfs(nbr)
            visited[node] = 2

        for name in self.tasks:
            if visited.get(name) is None:
                dfs(name)

    def _topological_layers(self):
        # build graph of dependents, indegree
        indegree = {n: 0 for n in self.tasks}
        graph = {n: [] for n in self.tasks}
        for n, t in self.tasks.items():
            for dep in t.dependencies:
                graph[dep].append(n)
                indegree[n] += 1
        layers = []
        indeg = indegree.copy()
        while indeg:
            zero = [n for n, d in indeg.items() if d == 0]
            if not zero:
                break
            layers.append(zero)
            for n in zero:
                for nbr in graph[n]:
                    indeg[nbr] -= 1
                indeg.pop(n)
        return layers

    def run(self):
        # scheduling
        if self.schedule:
            if not self.schedule.should_run():
                return {}
            else:
                self.schedule.last_run = datetime.datetime.now()

        self.validate()
        start_wf = datetime.datetime.now()
        failed = False

        layers = self._topological_layers()

        # execute layers
        for layer in layers:
            # prepare tasks to run in this layer
            to_run = []
            for name in layer:
                t = self.tasks[name]
                # if already succeeded, skip
                if t.state == TaskState.SUCCESS:
                    continue
                # if any dep failed, mark this failed
                dep_failed = any(
                    self.tasks[d].state == TaskState.FAILURE for d in t.dependencies
                )
                if dep_failed:
                    t.state = TaskState.FAILURE
                    t.error = Exception("Dependency failed")
                    failed = True
                    continue
                # schedule only pending or retrying
                if t.state in (TaskState.PENDING, TaskState.RETRYING):
                    to_run.append(t)
            if failed:
                break
            if not to_run:
                continue
            # run tasks in parallel
            with ThreadPoolExecutor(max_workers=len(to_run)) as exe:
                futures = {exe.submit(t.execute, self._build_context(t)): t for t in to_run}
                for fut in as_completed(futures):
                    t = futures[fut]
                    # after execute, check if failed
                    if t.state == TaskState.FAILURE:
                        failed = True
            if failed:
                break

        end_wf = datetime.datetime.now()
        # collect task executions
        task_execs = {}
        for name, t in self.tasks.items():
            if t.execution_records:
                # take last record
                task_execs[name] = t.execution_records[-1]
        status = "success" if not failed else "failure"
        self.execution_history.append(
            WorkflowExecution(start_wf, end_wf, status, task_execs)
        )
        if failed:
            raise TaskFailedError("Workflow failed")
        # return results
        results = {name: t.result for name, t in self.tasks.items()}
        return results

    def _build_context(self, task):
        # merge dicts from dependencies
        ctx = {}
        for dep in task.dependencies:
            res = self.tasks[dep].result
            if isinstance(res, dict):
                ctx.update(res)
        return ctx
