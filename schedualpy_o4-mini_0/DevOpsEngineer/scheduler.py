import threading
import uuid
from datetime import datetime, timedelta, timezone
from enum import Enum
from zoneinfo import ZoneInfo


class TaskStatus(Enum):
    SCHEDULED = "scheduled"
    RUNNING = "running"
    PAUSED = "paused"
    CANCELED = "canceled"
    COMPLETED = "completed"


class Task:
    def __init__(self, func, args=None, kwargs=None, *,
                 cron_expr=None, run_at=None, tz="UTC", priority=0, task_id=None):
        self.id = task_id or str(uuid.uuid4())
        self.func = func
        self.args = args or ()
        self.kwargs = kwargs or {}
        self.cron_expr = cron_expr
        self.one_off = run_at is not None
        self.tz = ZoneInfo(tz)
        self.run_at = None
        if run_at:
            # Normalize run_at to this task's timezone
            if run_at.tzinfo is None:
                run_at = run_at.replace(tzinfo=self.tz)
            else:
                run_at = run_at.astimezone(self.tz)
            # Store run_at in UTC
            self.run_at = run_at.astimezone(timezone.utc)
        self.next_run = None
        self._compute_next_run()
        self.priority = priority
        self.pre_hooks = []
        self.post_hooks = []
        self.dependencies = set()
        self.dependents = set()
        self.status = TaskStatus.SCHEDULED

    def _compute_next_run(self):
        now = datetime.now(timezone.utc)
        if self.one_off:
            self.next_run = self.run_at
        elif self.cron_expr:
            # Basic support for "* * * * *": schedule next minute at zero seconds
            base = now.astimezone(self.tz)
            nxt = (base + timedelta(minutes=1)).replace(second=0, microsecond=0)
            self.next_run = nxt.astimezone(timezone.utc)
        else:
            self.next_run = None

    def reschedule(self, cron_expr=None, run_at=None, tz=None):
        if cron_expr is not None:
            self.cron_expr = cron_expr
            self.one_off = False
        if run_at is not None:
            if run_at.tzinfo is None:
                # use provided tz or existing
                use_tz = ZoneInfo(tz) if tz else self.tz
                run_at = run_at.replace(tzinfo=use_tz)
            else:
                run_at = run_at.astimezone(ZoneInfo(tz)) if tz else run_at
            self.run_at = run_at.astimezone(timezone.utc)
            self.one_off = True
        if tz is not None:
            self.tz = ZoneInfo(tz)
        self._compute_next_run()

    def add_dependency(self, dep_task):
        self.dependencies.add(dep_task.id)
        dep_task.dependents.add(self.id)

    def run(self):
        self.status = TaskStatus.RUNNING
        for hook in self.pre_hooks:
            try:
                hook(self)
            except Exception:
                pass
        try:
            self.func(*self.args, **self.kwargs)
        except Exception:
            pass
        for hook in self.post_hooks:
            try:
                hook(self)
            except Exception:
                pass
        if self.one_off:
            self.status = TaskStatus.COMPLETED
            self.next_run = None
        else:
            self._compute_next_run()
            self.status = TaskStatus.SCHEDULED


class Scheduler:
    def __init__(self):
        self.tasks = {}
        self.lock = threading.Lock()

    def add_task(self, func, args=None, kwargs=None, *,
                 cron_expr=None, run_at=None, tz="UTC", priority=0, task_id=None):
        with self.lock:
            task = Task(func, args, kwargs,
                        cron_expr=cron_expr, run_at=run_at,
                        tz=tz, priority=priority, task_id=task_id)
            self.tasks[task.id] = task
            return task.id

    def register_pre_hook(self, task_id, hook):
        with self.lock:
            self.tasks[task_id].pre_hooks.append(hook)

    def register_post_hook(self, task_id, hook):
        with self.lock:
            self.tasks[task_id].post_hooks.append(hook)

    def add_dependency(self, task_id, dep_task_id):
        with self.lock:
            t = self.tasks[task_id]
            d = self.tasks[dep_task_id]
            t.add_dependency(d)

    def set_priority(self, task_id, priority):
        with self.lock:
            self.tasks[task_id].priority = priority

    def pause_task(self, task_id):
        with self.lock:
            t = self.tasks[task_id]
            if t.status == TaskStatus.SCHEDULED:
                t.status = TaskStatus.PAUSED

    def resume_task(self, task_id):
        with self.lock:
            t = self.tasks[task_id]
            if t.status == TaskStatus.PAUSED:
                t.status = TaskStatus.SCHEDULED

    def cancel_task(self, task_id):
        with self.lock:
            t = self.tasks[task_id]
            t.status = TaskStatus.CANCELED
            t.next_run = None

    def reschedule_task(self, task_id, *, cron_expr=None, run_at=None, tz=None):
        with self.lock:
            t = self.tasks[task_id]
            t.reschedule(cron_expr=cron_expr, run_at=run_at, tz=tz)

    def run_pending(self):
        # Continuously run tasks as they become due (handles dependencies)
        while True:
            now = datetime.now(timezone.utc)
            due = []
            with self.lock:
                for t in self.tasks.values():
                    if (t.status == TaskStatus.SCHEDULED and
                        t.next_run and t.next_run <= now and
                        all(self.tasks[dep].status == TaskStatus.COMPLETED for dep in t.dependencies)):
                        due.append(t)
            if not due:
                break
            # sort by priority desc, then by next_run time
            due.sort(key=lambda x: (-x.priority, x.next_run))
            for t in due:
                with self.lock:
                    if t.status != TaskStatus.SCHEDULED:
                        continue
                    if not t.next_run or t.next_run > now:
                        continue
                    if not all(self.tasks[dep].status == TaskStatus.COMPLETED for dep in t.dependencies):
                        continue
                    t.run()


# Documentation examples:

def example_k8s_rolling_update():
    # Placeholder for actual k8s rolling update logic
    pass

def example_docker_image_sweep():
    # Placeholder for actual docker sweep logic
    pass

def example_cloud_snapshot():
    # Placeholder for actual cloud snapshot logic
    pass
