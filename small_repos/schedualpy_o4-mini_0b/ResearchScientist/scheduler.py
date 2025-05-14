import threading
import time
from datetime import datetime, timedelta, timezone
from typing import Callable, List, Optional, Dict, Any


class Task:
    def __init__(
        self,
        task_id: str,
        func: Callable,
        *,
        cron: Optional[str] = None,
        interval: Optional[float] = None,
        one_off: Optional[datetime] = None,
        dependencies: Optional[List[str]] = None,
        priority: int = 0,
    ):
        self.task_id = task_id
        self.func = func
        self.cron = cron
        self.interval = interval
        self.one_off = one_off
        self.dependencies = dependencies or []
        self.priority = priority
        self.pre_hooks: List[Callable] = []
        self.post_hooks: List[Callable] = []
        self.state = "pending"
        self.last_run: Optional[datetime] = None
        self.next_run: Optional[datetime] = None
        self._compute_next_run(initial=True)

    def _parse_cron_interval(self, expr: str) -> float:
        # supports only minute-based */N * * * * expressions
        parts = expr.split()
        if len(parts) != 5:
            raise ValueError("Invalid cron expression")
        minute = parts[0]
        if minute.startswith("*/"):
            n = int(minute[2:])
            return n * 60
        if minute == "*":
            return 60
        # fixed minute (at mm past each hour)
        m = int(minute)
        now = datetime.now(timezone.utc)
        target = now.replace(minute=m, second=0, microsecond=0)
        if target <= now:
            target += timedelta(hours=1)
        return (target - now).total_seconds()

    def _compute_next_run(self, initial: bool = False):
        now = datetime.now(timezone.utc)
        if self.one_off:
            # schedule once
            dt = self.one_off.astimezone(timezone.utc)
            if initial:
                self.next_run = dt
        elif self.cron:
            interval = self._parse_cron_interval(self.cron)
            if initial or self.next_run is None:
                self.next_run = now + timedelta(seconds=interval)
            else:
                self.next_run = self.next_run + timedelta(seconds=interval)
        elif self.interval is not None:
            if initial or self.next_run is None:
                self.next_run = now + timedelta(seconds=self.interval)
            else:
                self.next_run = self.next_run + timedelta(seconds=self.interval)

    def should_run(self):
        now = datetime.now(timezone.utc)
        return (
            self.state == "pending"
            and self.next_run is not None
            and now >= self.next_run
        )


class Scheduler:
    def __init__(self):
        self.tasks: Dict[str, Task] = {}
        self.lock = threading.Lock()
        self.running = False

    def register_task(
        self,
        task_id: str,
        func: Callable,
        *,
        cron: Optional[str] = None,
        interval: Optional[float] = None,
        one_off: Optional[datetime] = None,
        dependencies: Optional[List[str]] = None,
        priority: int = 0,
    ):
        with self.lock:
            if task_id in self.tasks:
                raise ValueError(f"Task {task_id} exists")
            task = Task(
                task_id,
                func,
                cron=cron,
                interval=interval,
                one_off=one_off,
                dependencies=dependencies,
                priority=priority,
            )
            self.tasks[task_id] = task

    def register_pre_post_hooks(
        self, task_id: str, pre_hooks: List[Callable], post_hooks: List[Callable]
    ):
        with self.lock:
            task = self.tasks[task_id]
            task.pre_hooks.extend(pre_hooks)
            task.post_hooks.extend(post_hooks)

    def set_task_priority(self, task_id: str, priority: int):
        with self.lock:
            self.tasks[task_id].priority = priority

    def start(self):
        with self.lock:
            self.running = True

    def pause_task(self, task_id: str):
        with self.lock:
            task = self.tasks[task_id]
            if task.state == "pending":
                task.state = "paused"

    def resume_task(self, task_id: str):
        with self.lock:
            task = self.tasks[task_id]
            if task.state == "paused":
                task.state = "pending"

    def cancel_task(self, task_id: str):
        with self.lock:
            task = self.tasks[task_id]
            task.state = "cancelled"

    def dynamic_reschedule(
        self,
        task_id: str,
        *,
        cron: Optional[str] = None,
        interval: Optional[float] = None,
        one_off: Optional[datetime] = None,
    ):
        with self.lock:
            task = self.tasks[task_id]
            if cron is not None:
                task.cron = cron
            if interval is not None:
                task.interval = interval
            if one_off is not None:
                task.one_off = one_off
            # reset state for rescheduled task
            task.state = "pending"
            task._compute_next_run(initial=True)

    def run_pending(self):
        # collect tasks to run
        with self.lock:
            if not self.running:
                return
            now = datetime.now(timezone.utc)
            # find all due tasks
            due_tasks = [
                task for task in self.tasks.values() if task.should_run()
            ]
            # include tasks whose dependencies are either already completed
            # or also due in this batch
            due_ids = {t.task_id for t in due_tasks}
            filtered = []
            for t in due_tasks:
                deps = t.dependencies or []
                ok = True
                for d in deps:
                    if d in due_ids:
                        continue
                    # if dependency already fully completed (one-off), allow
                    if self.tasks[d].state == "completed":
                        continue
                    ok = False
                    break
                if ok:
                    filtered.append(t)

            # build dependency graph among filtered tasks
            tasks_map = {t.task_id: t for t in filtered}
            in_degree: Dict[str, int] = {}
            graph: Dict[str, List[str]] = {}
            for t in filtered:
                in_deg = 0
                for d in t.dependencies:
                    if d in tasks_map:
                        in_deg += 1
                        graph.setdefault(d, []).append(t.task_id)
                in_degree[t.task_id] = in_deg

            # Kahn's algorithm with priority tie-breaker
            ready = [
                tasks_map[tid]
                for tid, deg in in_degree.items()
                if deg == 0
            ]
            ordered: List[Task] = []
            # sort helper
            def sort_key(task: Task):
                return (-task.priority, task.next_run)

            while ready:
                ready.sort(key=sort_key)
                current = ready.pop(0)
                ordered.append(current)
                for nbr in graph.get(current.task_id, []):
                    in_degree[nbr] -= 1
                    if in_degree[nbr] == 0:
                        ready.append(tasks_map[nbr])

        # execute tasks in order
        for task in ordered:
            with self.lock:
                task.state = "running"
            try:
                for hook in task.pre_hooks:
                    hook()
                task.func()
                for hook in task.post_hooks:
                    hook()
                with self.lock:
                    now_run = datetime.now(timezone.utc)
                    task.last_run = now_run
                    if task.one_off:
                        task.state = "completed"
                        task.next_run = None
                    else:
                        # recurring task: ready for next cycle
                        task.state = "pending"
                        task._compute_next_run()
            except Exception:
                with self.lock:
                    task.state = "failed"

    def get_task_state(self, task_id: str) -> str:
        with self.lock:
            return self.tasks[task_id].state

    def get_next_run(self, task_id: str) -> Optional[datetime]:
        with self.lock:
            return self.tasks[task_id].next_run
