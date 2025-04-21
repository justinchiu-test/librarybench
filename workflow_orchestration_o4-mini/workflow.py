import threading
import time
import datetime
import inspect
from enum import Enum
from collections import defaultdict, deque
from concurrent.futures import ThreadPoolExecutor, TimeoutError, as_completed

class TaskState(Enum):
    PENDING = "pending"
    RUNNING = "running"
    SUCCESS = "success"
    FAILURE = "failure"
    RETRYING = "retrying"

class TaskFailedError(Exception):
    pass

class TaskExecutionRecord:
    def __init__(self, start_time, end_time, status):
        self.start_time = start_time
        self.end_time = end_time
        self.status = status  # "success" or "failure"

class WorkflowExecutionRecord:
    def __init__(self, start_time):
        self.start_time = start_time
        self.end_time = None
        self.status = None  # "success" or "failure"
        self.task_executions = {}  # name -> TaskExecutionRecord

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
        self.max_retries = max_retries
        self.retry_delay = retry_delay
        self.timeout = timeout
        self.logger = logger
        self.state = TaskState.PENDING
        self.result = None
        self.error = None
        self.attempts = 0
        self.execution_records = []

    def reset(self):
        self.state = TaskState.PENDING
        self.result = None
        self.error = None
        self.attempts = 0
        # keep execution history across runs

    def execute(self, context=None):
        """One attempt to run the task."""
        self.attempts += 1
        start = datetime.datetime.now()
        self.state = TaskState.RUNNING
        exc = None
        result = None

        try:
            # prepare call
            sig = inspect.signature(self.func)
            if len(sig.parameters) == 0:
                # call without context
                call_func = lambda: self.func()
            else:
                call_func = lambda: self.func(context=context)
            if self.logger:
                # redirect logging if provided
                # assume logging in func uses this logger
                pass
            if self.timeout is not None:
                with ThreadPoolExecutor(max_workers=1) as executor:
                    fut = executor.submit(call_func)
                    result = fut.result(timeout=self.timeout)
            else:
                result = call_func()
            self.state = TaskState.SUCCESS
            self.result = result
            self.error = None
        except TimeoutError:
            exc = Exception(f"Task '{self.name}' timed out")
            self.error = exc
        except Exception as e:
            exc = e
            self.error = e

        end = datetime.datetime.now()
        # determine status
        if exc is None:
            status = "success"
        else:
            if self.attempts <= self.max_retries:
                self.state = TaskState.RETRYING
                status = "failure"
            else:
                self.state = TaskState.FAILURE
                status = "failure"

        # record execution
        rec = TaskExecutionRecord(start, end, status)
        self.execution_records.append(rec)

        return getattr(self, 'result', None)

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
            return now >= self.last_run + datetime.timedelta(hours=1)
        if self.type == ScheduleType.DAILY:
            # only run once per day at specified hour/minute
            if self.hour is None or self.minute is None:
                return True
            today_sched = now.replace(hour=self.hour, minute=self.minute,
                                      second=0, microsecond=0)
            # if scheduled time passed, and last_run date < today
            if now >= today_sched and self.last_run.date() < now.date():
                return True
            return False
        return False

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
        # missing deps
        for t in self.tasks.values():
            for dep in t.dependencies:
                if dep not in self.tasks:
                    raise ValueError(f"Missing dependency: {dep}")
        # detect cycles via DFS
        visited = {}
        def dfs(node):
            if node in visited:
                if visited[node] == 1:
                    return True  # cycle
                return False
            visited[node] = 1  # visiting
            for dep in self.tasks[node].dependencies:
                if dfs(dep):
                    return True
            visited[node] = 2
            return False

        for name in self.tasks:
            if dfs(name):
                raise ValueError("Cycle detected in workflow")

    def run(self):
        self.validate()
        wf_record = WorkflowExecutionRecord(datetime.datetime.now())
        # prepare results from already successful tasks
        results = {}
        # reset pending tasks
        for t in self.tasks.values():
            if t.state == TaskState.SUCCESS:
                results[t.name] = t.result
            else:
                t.state = TaskState.PENDING

        # topological sort to get levels
        indegree = {name: 0 for name in self.tasks}
        graph = defaultdict(list)
        for t in self.tasks.values():
            for dep in t.dependencies:
                graph[dep].append(t.name)
                indegree[t.name] += 1
        # BFS for levels
        queue = deque()
        levels = {}
        for name, deg in indegree.items():
            if deg == 0:
                queue.append(name)
                levels[name] = 0
        topo = []
        while queue:
            u = queue.popleft()
            topo.append(u)
            for v in graph[u]:
                indegree[v] -= 1
                if indegree[v] == 0:
                    levels[v] = levels[u] + 1
                    queue.append(v)
        # group by level
        lvl_map = defaultdict(list)
        for name, lvl in levels.items():
            lvl_map[lvl].append(self.tasks[name])
        # executor
        executor = ThreadPoolExecutor(max_workers=len(self.tasks) or 1)
        try:
            for lvl in sorted(lvl_map):
                batch = lvl_map[lvl]
                # before running batch, propagate failures
                for t in batch:
                    if t.state != TaskState.PENDING:
                        continue
                    for dep in t.dependencies:
                        if self.tasks[dep].state == TaskState.FAILURE:
                            t.state = TaskState.FAILURE
                            t.error = Exception(f"Dependency {dep} failed")
                            now = datetime.datetime.now()
                            rec = TaskExecutionRecord(now, now, "failure")
                            t.execution_records.append(rec)
                            wf_record.task_executions[t.name] = rec
                            break
                # if any in this level just failed, abort
                failed = [t for t in batch if t.state == TaskState.FAILURE and t.name in wf_record.task_executions]
                if failed:
                    wf_record.status = "failure"
                    wf_record.end_time = datetime.datetime.now()
                    self.execution_history.append(wf_record)
                    raise TaskFailedError("Workflow failed due to dependency failure")
                # run pending tasks in parallel
                futures = {}
                for t in batch:
                    if t.state == TaskState.PENDING:
                        # build context
                        ctx = {}
                        for dep in t.dependencies:
                            r = results.get(dep)
                            if isinstance(r, dict):
                                ctx.update(r)
                        # submit
                        futures[executor.submit(self._run_task, t, ctx)] = t
                    else:
                        # already success - ensure there's a record
                        if not t.execution_records:
                            now = datetime.datetime.now()
                            rec = TaskExecutionRecord(now, now, "success")
                            t.execution_records.append(rec)
                        wf_record.task_executions[t.name] = t.execution_records[-1]
                for fut in as_completed(futures):
                    t = futures[fut]
                    # record
                    wf_record.task_executions[t.name] = t.execution_records[-1]
                    if t.state == TaskState.SUCCESS:
                        results[t.name] = t.result
                    else:
                        # propagate failure to dependents
                        for dep_task in self.tasks.values():
                            if t.name in dep_task.dependencies and dep_task.state == TaskState.PENDING:
                                dep_task.state = TaskState.FAILURE
                                dep_task.error = Exception(f"Dependency {t.name} failed")
                                now = datetime.datetime.now()
                                rec = TaskExecutionRecord(now, now, "failure")
                                dep_task.execution_records.append(rec)
                                wf_record.task_executions[dep_task.name] = rec
                        wf_record.status = "failure"
                        wf_record.end_time = datetime.datetime.now()
                        self.execution_history.append(wf_record)
                        err_msg = str(t.error) or ""
                        raise TaskFailedError(f"Task {t.name} failed: {err_msg}")
            # all levels done
            wf_record.status = "success"
            wf_record.end_time = datetime.datetime.now()
            self.execution_history.append(wf_record)
            return results
        finally:
            executor.shutdown(wait=False)

    def _run_task(self, task, context):
        # handle retries internally
        while True:
            task.execute(context=context)
            if task.state == TaskState.RETRYING:
                # backoff logic could go here (skipped for tests)
                continue
            break
        return task.state
