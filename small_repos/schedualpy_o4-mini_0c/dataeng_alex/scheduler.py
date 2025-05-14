import threading
import time
import random
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

class Task:
    def __init__(self, task_id, func, cron_expr=None, run_at=None, tz='UTC', jitter_seconds=0, group=None):
        self.task_id = task_id
        self.func = func
        self.cron_expr = cron_expr  # in seconds for simplicity
        self.run_at = run_at        # datetime for one-off
        self.tz = tz
        self.jitter_seconds = jitter_seconds
        self.group = group
        self.enabled = True
        self.next_run = None
        # track whether it's the first scheduled run (to skip jitter on first run)
        self.first_run = True
        self.compute_next_run()

    def compute_next_run(self):
        now = datetime.now(ZoneInfo(self.tz))
        if self.run_at:
            # one-off scheduling uses the exact run_at
            self.next_run = self.run_at
        elif self.cron_expr is not None:
            # on first run, do not apply jitter; afterward apply ± jitter
            if self.first_run or self.jitter_seconds == 0:
                jitter = 0
            else:
                jitter = random.uniform(-self.jitter_seconds, self.jitter_seconds)
            self.next_run = now + timedelta(seconds=self.cron_expr + jitter)
            # mark that we've scheduled the first run
            self.first_run = False
        else:
            self.next_run = None

class ThreadSafeScheduler:
    def __init__(self):
        self.tasks = {}
        self.task_groups = {}  # group_name -> {'tasks': set, 'paused': bool}
        self.plugins = {}
        self.metrics = {
            'job_durations': {},
            'success_counts': {},
            'failure_counts': {},
            'schedule_lag': {},
        }
        self.pre_hooks = {}
        self.post_hooks = {}
        self.lock = threading.Lock()

    def schedule(self, task_id, func, cron_expr, tz='UTC', jitter_seconds=0, group=None):
        with self.lock:
            task = Task(task_id, func, cron_expr=cron_expr, tz=tz,
                        jitter_seconds=jitter_seconds, group=group)
            self.tasks[task_id] = task
            if group:
                self._add_task_to_group(task_id, group)
            return task

    def schedule_one_off(self, task_id, func, run_at, tz='UTC', jitter_seconds=0, group=None):
        with self.lock:
            if run_at.tzinfo is None:
                run_at = run_at.replace(tzinfo=ZoneInfo(tz))
            task = Task(task_id, func, run_at=run_at, tz=tz,
                        jitter_seconds=jitter_seconds, group=group)
            self.tasks[task_id] = task
            if group:
                self._add_task_to_group(task_id, group)
            return task

    def reschedule(self, task_id, new_cron_expr):
        with self.lock:
            task = self.tasks.get(task_id)
            if not task:
                raise KeyError(f"No such task {task_id}")
            task.cron_expr = new_cron_expr
            task.run_at = None
            # treat as a new series, so allow skipping jitter on next compute
            task.first_run = True
            task.compute_next_run()
            return task

    def cancel(self, task_id):
        with self.lock:
            task = self.tasks.pop(task_id, None)
            if not task:
                raise KeyError(f"No such task {task_id}")
            if task.group:
                grp = self.task_groups.get(task.group)
                if grp:
                    grp['tasks'].discard(task_id)

    def register_pre_hook(self, task_id, hook):
        with self.lock:
            self.pre_hooks.setdefault(task_id, []).append(hook)

    def register_post_hook(self, task_id, hook):
        with self.lock:
            self.post_hooks.setdefault(task_id, []).append(hook)

    def load_plugin(self, plugin_name, plugin_callable):
        with self.lock:
            self.plugins[plugin_name] = plugin_callable

    def create_task_group(self, group_name):
        with self.lock:
            if group_name in self.task_groups:
                raise KeyError(f"Group {group_name} exists")
            self.task_groups[group_name] = {'tasks': set(), 'paused': False}

    def pause_group(self, group_name):
        with self.lock:
            grp = self.task_groups.get(group_name)
            if not grp:
                raise KeyError(f"No such group {group_name}")
            grp['paused'] = True

    def resume_group(self, group_name):
        with self.lock:
            grp = self.task_groups.get(group_name)
            if not grp:
                raise KeyError(f"No such group {group_name}")
            grp['paused'] = False

    def emit_metrics(self):
        with self.lock:
            # return a shallow copy
            return {
                'job_durations': dict(self.metrics['job_durations']),
                'success_counts': dict(self.metrics['success_counts']),
                'failure_counts': dict(self.metrics['failure_counts']),
                'schedule_lag': dict(self.metrics['schedule_lag']),
            }

    def _add_task_to_group(self, task_id, group):
        grp = self.task_groups.get(group)
        if not grp:
            self.task_groups[group] = {'tasks': set(), 'paused': False}
            grp = self.task_groups[group]
        grp['tasks'].add(task_id)

    def _run_task(self, task):
        start = time.time()
        scheduled_time = task.next_run
        lag = time.time() - scheduled_time.timestamp() if scheduled_time else 0
        # pre-hooks
        for hook in self.pre_hooks.get(task.task_id, []):
            hook(task.task_id)
        # run
        try:
            task.func()
            success = True
        except Exception:
            success = False
        duration = time.time() - start
        # post-hooks
        for hook in self.post_hooks.get(task.task_id, []):
            hook(task.task_id)
        # metrics update
        with self.lock:
            self.metrics['job_durations'].setdefault(task.task_id, []).append(duration)
            self.metrics['schedule_lag'].setdefault(task.task_id, []).append(lag)
            if success:
                self.metrics['success_counts'][task.task_id] = self.metrics['success_counts'].get(task.task_id, 0) + 1
            else:
                self.metrics['failure_counts'][task.task_id] = self.metrics['failure_counts'].get(task.task_id, 0) + 1

    def _run_pending(self):
        utc = ZoneInfo('UTC')
        now = datetime.now(utc)
        to_run = []
        with self.lock:
            for task in list(self.tasks.values()):
                grp = task.group and self.task_groups.get(task.group)
                if not task.enabled:
                    continue
                if grp and grp['paused']:
                    continue
                if task.next_run:
                    # normalize to UTC for comparison
                    nrun = task.next_run
                    if nrun.tzinfo is None:
                        nrun = nrun.replace(tzinfo=utc)
                    else:
                        nrun = nrun.astimezone(utc)
                    if nrun <= now:
                        to_run.append(task)
        for task in to_run:
            threading.Thread(target=self._run_task, args=(task,)).start()
            with self.lock:
                # reschedule or remove
                if task.cron_expr is not None:
                    task.compute_next_run()
                else:
                    self.tasks.pop(task.task_id, None)

    def start(self, interval=1):
        self._stop = False
        def loop():
            while not getattr(self, '_stop', False):
                self._run_pending()
                time.sleep(interval)
        t = threading.Thread(target=loop, daemon=True)
        t.start()
        return t

    def stop(self):
        self._stop = True
