import threading
import time
import datetime
from datetime import datetime, timedelta, timezone
import re

class Task:
    def __init__(self, name, func, cron=None, run_at=None, interval=None,
                 dependencies=None, priority=0, tz=timezone.utc, one_off=False):
        self.name = name
        self.func = func
        self.cron = cron
        self.run_at = run_at
        self.interval = interval
        self.dependencies = set(dependencies) if dependencies else set()
        self.priority = priority
        self.tz = tz
        self.one_off = one_off
        self.next_run = None
        # track last execution status; start as False so dependencies wait until real run
        self.last_status = False
        self.paused = False
        self.canceled = False
        self._compute_next_run()

    def _compute_next_run(self):
        now = datetime.now(self.tz)
        if self.canceled:
            self.next_run = None
            return
        if self.one_off:
            self.next_run = self.run_at
        elif self.cron:
            # support minute field only: '*/n * * * *'
            parts = self.cron.strip().split()
            if len(parts) != 5:
                raise ValueError("Invalid cron expression")
            minute = parts[0]
            match = re.match(r'\*/(\d+)', minute)
            if match:
                interval_min = int(match.group(1))
                interval = timedelta(minutes=interval_min)
                if not self.next_run:
                    self.next_run = now + interval
                else:
                    while self.next_run <= now:
                        self.next_run += interval
            else:
                # exact minute
                minute_val = int(minute) if minute != '*' else now.minute
                run = now.replace(minute=minute_val, second=0, microsecond=0)
                if run <= now:
                    run += timedelta(hours=1)
                self.next_run = run
        elif self.interval is not None:
            if not self.next_run:
                self.next_run = now + timedelta(seconds=self.interval)
            else:
                while self.next_run <= now:
                    self.next_run += timedelta(seconds=self.interval)
        else:
            self.next_run = None

class Scheduler:
    def __init__(self):
        self.tasks = {}
        self.pre_hook = None
        self.post_hook = None
        self.lock = threading.Lock()

    def register_pre_post_hooks(self, pre_hook=None, post_hook=None):
        with self.lock:
            self.pre_hook = pre_hook
            self.post_hook = post_hook

    def schedule_cron(self, name, func, cron_expr, dependencies=None,
                      priority=0, tz=timezone.utc):
        with self.lock:
            task = Task(name, func, cron=cron_expr, dependencies=dependencies,
                        priority=priority, tz=tz)
            self.tasks[name] = task

    def schedule_interval(self, name, func, interval_seconds, dependencies=None,
                          priority=0):
        with self.lock:
            task = Task(name, func, interval=interval_seconds,
                        dependencies=dependencies, priority=priority)
            self.tasks[name] = task

    def schedule_one_off(self, name, func, run_at, dependencies=None,
                         priority=0, tz=timezone.utc):
        with self.lock:
            run_at = run_at.astimezone(tz)
            task = Task(name, func, run_at=run_at, dependencies=dependencies,
                        priority=priority, tz=tz, one_off=True)
            self.tasks[name] = task

    def declare_task_dependencies(self, name, dependencies):
        with self.lock:
            if name in self.tasks:
                self.tasks[name].dependencies.update(dependencies)

    def set_task_priority(self, name, priority):
        with self.lock:
            if name in self.tasks:
                self.tasks[name].priority = priority

    def control_task_runtime(self, name, action):
        with self.lock:
            task = self.tasks.get(name)
            if not task:
                return
            if action == 'pause':
                task.paused = True
            elif action == 'resume':
                task.paused = False
            elif action == 'cancel':
                task.canceled = True
                task.next_run = None
            elif action == 'start':
                task.paused = False
                task.canceled = False
                # reset scheduling
                task.next_run = None
                task._compute_next_run()

    def dynamic_reschedule(self, name, cron_expr=None, interval_seconds=None,
                           run_at=None):
        with self.lock:
            task = self.tasks.get(name)
            if not task:
                return
            if cron_expr is not None:
                task.cron = cron_expr
                task.interval = None
                task.one_off = False
            if interval_seconds is not None:
                task.interval = interval_seconds
                task.cron = None
                task.one_off = False
            if run_at is not None:
                task.run_at = run_at.astimezone(task.tz)
                task.one_off = True
            # force recompute from now
            task.next_run = None
            task._compute_next_run()

    def get_next_run(self, name):
        with self.lock:
            task = self.tasks.get(name)
            return task.next_run if task else None

    def run_pending(self):
        # gather ready tasks with dependencies satisfied
        with self.lock:
            now = datetime.now(timezone.utc)
            ready = []
            for t in self.tasks.values():
                if t.next_run and t.next_run <= now and not t.paused and not t.canceled:
                    # check dependencies based on last_status before this run
                    deps_unsatisfied = False
                    for dep in t.dependencies:
                        dep_task = self.tasks.get(dep)
                        if not dep_task or not dep_task.last_status:
                            deps_unsatisfied = True
                            break
                    if not deps_unsatisfied:
                        ready.append(t)
            # sort by priority descending
            ready.sort(key=lambda x: -x.priority)
        # execute tasks outside lock
        for task in ready:
            try:
                if self.pre_hook:
                    self.pre_hook(task.name)
                task.func()
                task.last_status = True
            except Exception:
                task.last_status = False
            finally:
                if self.post_hook:
                    self.post_hook(task.name)
            with self.lock:
                if task.one_off:
                    # mark as done
                    task.next_run = None
                else:
                    task._compute_next_run()

    # documentation examples
    def example_mqtt_pipeline(self):
        """
        Example: schedule sensor polling with MQTT publish
        """
        pass

    def example_edge_to_cloud_batch(self):
        """
        Example: batch collect and push to cloud
        """
        pass

    def example_autoscale_trigger(self):
        """
        Example: trigger autoscale based on load
        """
        pass
