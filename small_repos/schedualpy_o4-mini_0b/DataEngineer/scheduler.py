import threading
import time
import datetime
import heapq
import uuid
from typing import Callable, List, Optional, Any, Dict
import pytz

# Try to import croniter; if unavailable, provide a dummy stub
try:
    from croniter import croniter
except ImportError:
    class _DummyCronIter:
        def __init__(self, expr, base):
            self.expr = expr
            self.base = base

        def get_next(self, _type=datetime.datetime):
            # Return a datetime (strip tzinfo if present)
            dt = self.base
            if dt.tzinfo is not None:
                # return naive datetime so that .replace happens in Task
                return dt.replace(tzinfo=None)
            return dt

    def croniter(expr, base):
        return _DummyCronIter(expr, base)


class TaskStatus:
    PENDING = "PENDING"
    RUNNING = "RUNNING"
    PAUSED = "PAUSED"
    CANCELED = "CANCELED"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"


class Task:
    def __init__(
        self,
        func: Callable,
        name: Optional[str] = None,
        cron: Optional[str] = None,
        interval: Optional[int] = None,
        timezone: str = "UTC",
        one_off: bool = False,
        priority: int = 0
    ):
        self.id = str(uuid.uuid4())
        self.func = func
        self.name = name or self.id
        self.cron = cron
        self.interval = interval
        # use our vendored pytz.timezone
        self.timezone = pytz.timezone(timezone)
        self.one_off = one_off
        self.priority = priority
        self.pre_hooks: List[Callable] = []
        self.post_hooks: List[Callable] = []
        self.dependencies: List['Task'] = []
        self.dependents: List['Task'] = []
        self.status = TaskStatus.PENDING
        self.next_run: Optional[datetime.datetime] = None
        self._compute_next_run()

    def add_pre_hook(self, hook: Callable):
        self.pre_hooks.append(hook)

    def add_post_hook(self, hook: Callable):
        self.post_hooks.append(hook)

    def add_dependency(self, task: 'Task'):
        self.dependencies.append(task)
        task.dependents.append(self)

    def _compute_next_run(self):
        # Align to whole-second boundaries so tasks scheduled "simultaneously" are equal
        now = datetime.datetime.now(self.timezone).replace(microsecond=0)
        if self.cron:
            base = now
            itr = croniter(self.cron, base)
            # croniter returns a datetime (naive or aware); attach timezone
            nr = itr.get_next(datetime.datetime)
            # always attach our timezone tzinfo
            self.next_run = nr.replace(tzinfo=self.timezone)
        elif self.interval:
            self.next_run = now + datetime.timedelta(seconds=self.interval)
        else:
            self.next_run = None

    def run(self):
        # skip canceled/paused
        if self.status in (TaskStatus.CANCELED, TaskStatus.PAUSED):
            return
        # skip if dependencies not done
        for dep in self.dependencies:
            if dep.status != TaskStatus.COMPLETED:
                return
        self.status = TaskStatus.RUNNING
        try:
            for hook in self.pre_hooks:
                hook(self)
            self.func(self)
            for hook in self.post_hooks:
                hook(self)
            self.status = TaskStatus.COMPLETED
        except Exception:
            self.status = TaskStatus.FAILED
        finally:
            # only compute next run for recurring tasks that completed successfully
            if not self.one_off and self.status == TaskStatus.COMPLETED:
                self._compute_next_run()


class Scheduler:
    def __init__(self):
        self.tasks: Dict[str, Task] = {}
        self.lock = threading.Lock()
        self._stop_event = threading.Event()
        self._heap: List[Any] = []
        self.thread = threading.Thread(target=self._run_loop, daemon=True)

    def start(self):
        self._stop_event.clear()
        if not self.thread.is_alive():
            self.thread = threading.Thread(target=self._run_loop, daemon=True)
            self.thread.start()

    def stop(self):
        self._stop_event.set()
        self.thread.join()

    def register_task(self, task: Task):
        with self.lock:
            self.tasks[task.id] = task
            if task.next_run:
                heapq.heappush(self._heap, (task.next_run, -task.priority, task.id))

    def register_pre_post_hooks(self, task: Task, pre: Optional[Callable] = None, post: Optional[Callable] = None):
        if pre:
            task.add_pre_hook(pre)
        if post:
            task.add_post_hook(post)

    def declare_task_dependencies(self, task: Task, depends_on: Task):
        task.add_dependency(depends_on)

    def set_task_priority(self, task: Task, priority: int):
        task.priority = priority

    def control_task_runtime(self, task: Task, action: str):
        with self.lock:
            if action == "pause":
                task.status = TaskStatus.PAUSED
            elif action == "resume":
                if task.status == TaskStatus.PAUSED:
                    task.status = TaskStatus.PENDING
                    # remove any stale scheduled entries for this task
                    self._heap = [
                        (rt, pr, tid) for (rt, pr, tid) in self._heap
                        if tid != task.id
                    ]
                    heapq.heapify(self._heap)
                    # schedule next run relative to now
                    task._compute_next_run()
                    if task.next_run:
                        heapq.heappush(self._heap, (task.next_run, -task.priority, task.id))
            elif action == "cancel":
                task.status = TaskStatus.CANCELED

    def dynamic_reschedule(self, task: Task, cron: Optional[str] = None, interval: Optional[int] = None):
        with self.lock:
            task.cron = cron
            task.interval = interval
            task._compute_next_run()
            if task.next_run:
                heapq.heappush(self._heap, (task.next_run, -task.priority, task.id))

    def _run_loop(self):
        while not self._stop_event.is_set():
            now = datetime.datetime.now(pytz.utc)
            with self.lock:
                # schedule all due tasks
                while self._heap and self._heap[0][0].astimezone(pytz.utc) <= now:
                    run_time, neg_prio, tid = heapq.heappop(self._heap)
                    task = self.tasks.get(tid)
                    if not task:
                        continue
                    # skip canceled or paused
                    if task.status in (TaskStatus.CANCELED, TaskStatus.PAUSED):
                        continue
                    # skip due to unmet dependencies: reschedule to next interval/cron
                    if task.dependencies and any(dep.status != TaskStatus.COMPLETED for dep in task.dependencies):
                        task._compute_next_run()
                        if not task.one_off and task.next_run and task.status != TaskStatus.CANCELED:
                            heapq.heappush(self._heap, (task.next_run, -task.priority, task.id))
                        continue
                    # run synchronously
                    task.run()
                    # reschedule if recurring and still active
                    if not task.one_off and task.next_run and task.status != TaskStatus.CANCELED:
                        heapq.heappush(self._heap, (task.next_run, -task.priority, task.id))
            time.sleep(0.5)
