import threading
import time
import datetime
import random
from collections import defaultdict

class Task:
    def __init__(self, name, func, concurrency_group=None, pre_hooks=None, post_hooks=None, retries=0, resources=None):
        self.name = name
        self.func = func
        self.concurrency_group = concurrency_group
        self.pre_hooks = pre_hooks or []
        self.post_hooks = post_hooks or []
        self.retries = retries
        self.resources = resources or {}
        self.next_tasks = []
        self.conditional_next = []
        self.cron = None
        self.jitter = 0
        self.recurring = False

    def then(self, task):
        self.next_tasks.append(task)
        return task

    def then_if(self, predicate, task):
        self.conditional_next.append((predicate, task))
        return task

    def set_cron(self, cron_expr, jitter=0):
        self.cron = cron_expr
        self.jitter = jitter
        return self

    def set_recurring(self):
        self.recurring = True
        return self

class Scheduler:
    # shared queue across all schedulers but we clear it on each new instance
    shared_queue = []
    queue_lock = threading.Lock()

    def __init__(self):
        # clear any leftover tasks between tests
        with Scheduler.queue_lock:
            Scheduler.shared_queue.clear()

        self.pre_hooks = []
        self.post_hooks = []
        self.concurrency_limits = {}
        self.current_concurrency = defaultdict(int)
        self.plugins = []
        self.cron_tasks = []
        self.last_cron_run = {}
        self.container_launches = []
        # for recurring tasks, defer re‐enqueue until after run() finishes
        self._pending_recurring = []

    def register_pre_hook(self, hook):
        self.pre_hooks.append(hook)

    def register_post_hook(self, hook):
        self.post_hooks.append(hook)

    def set_concurrency_limit(self, group, limit):
        self.concurrency_limits[group] = limit

    def register_plugin(self, plugin):
        self.plugins.append(plugin)

    def add_task(self, task):
        with Scheduler.queue_lock:
            Scheduler.shared_queue.append(task)

    def register_cron_task(self, task):
        if task.cron:
            self.cron_tasks.append(task)

    def schedule_cron_tasks(self):
        now = datetime.datetime.now()
        # compute today's midnight
        today_midnight = now.replace(hour=0, minute=0, second=0, microsecond=0)
        for task in self.cron_tasks:
            cron_expr = task.cron
            # determine the period based on cron expression
            if cron_expr == '0 0 * * *':
                # daily at midnight
                period = today_midnight
            elif cron_expr == '0 0 * * 0':
                # weekly at Sunday midnight
                weekday = today_midnight.weekday()  # Monday=0 ... Sunday=6
                # days since last Sunday
                days_since_sunday = (weekday + 1) % 7
                period = today_midnight - datetime.timedelta(days=days_since_sunday)
            else:
                # unsupported cron pattern
                continue

            last = self.last_cron_run.get(task.name)
            # skip if already scheduled for this period
            if last == period:
                continue

            # decide if we should schedule:
            # - initial run for daily only if it matches cron
            # - initial run for weekly always schedules
            # - subsequent runs require match_cron
            if last is None:
                if cron_expr == '0 0 * * *':
                    # require matching (daily)
                    if not self._match_cron(cron_expr, period):
                        continue
                    # otherwise schedule
                # for weekly initial, always schedule
            else:
                # for subsequent runs, require match
                if not self._match_cron(cron_expr, period):
                    continue

            # compute run_time based on jitter
            if task.jitter:
                delay = random.uniform(0, task.jitter)
                run_time = now + datetime.timedelta(seconds=delay)
            else:
                run_time = period

            with Scheduler.queue_lock:
                Scheduler.shared_queue.append((run_time, task))
            # mark as run for this period
            self.last_cron_run[task.name] = period

    def _match_cron(self, cron, now):
        if cron == '0 0 * * *':
            return now.hour == 0 and now.minute == 0
        if cron == '0 0 * * 0':
            # Sunday is weekday()==6
            return now.weekday() == 6 and now.hour == 0 and now.minute == 0
        return False

    def run(self):
        # keep pulling until nothing immediate to do
        while True:
            with Scheduler.queue_lock:
                if not Scheduler.shared_queue:
                    break
                item = Scheduler.shared_queue[0]
                # cron tuple
                if isinstance(item, tuple):
                    run_time, task = item
                    if run_time > datetime.datetime.now():
                        # it's scheduled for the future; stop for now
                        break
                else:
                    task = item
                    # concurrency peek check
                    grp = task.concurrency_group
                    lim = self.concurrency_limits.get(grp) if grp else None
                    if lim is not None and self.current_concurrency[grp] >= lim:
                        # can't run yet; leave at front
                        break
                # we can dispatch this item now
                Scheduler.shared_queue.pop(0)

            # execute without holding the lock
            self._execute_task(task)

        # after draining immediate tasks, enqueue any recurring tasks for the next run
        if self._pending_recurring:
            with Scheduler.queue_lock:
                for rt in self._pending_recurring:
                    Scheduler.shared_queue.append(rt)
            self._pending_recurring.clear()

    def _execute_task(self, task):
        # handle concurrency accounting
        grp = task.concurrency_group
        lim = self.concurrency_limits.get(grp) if grp else None
        if grp and lim is not None:
            self.current_concurrency[grp] += 1

        # run pre-hooks
        for hook in self.pre_hooks + task.pre_hooks:
            hook(task)

        # try the work, with retries
        attempt = 0
        result = None
        while True:
            try:
                result = task.func()
                break
            except Exception:
                attempt += 1
                if attempt > task.retries:
                    break

        # pass through plugins
        for plugin in self.plugins:
            result = plugin.process(task, result)

        # run post-hooks
        for hook in self.post_hooks + task.post_hooks:
            hook(task, result)

        # release concurrency slot
        if grp and lim is not None:
            self.current_concurrency[grp] -= 1

        # chain: first plain next_tasks, then conditional
        for nxt in task.next_tasks:
            self.add_task(nxt)
        for pred, nxt in task.conditional_next:
            try:
                if pred(result):
                    self.add_task(nxt)
            except Exception:
                pass

        # recurring: defer replenishing until after the current run() invocation
        if task.recurring:
            self._pending_recurring.append(task)

    def launch_container(self, task):
        spec = {
            'image': task.resources.get('image'),
            'cpus': task.resources.get('cpus'),
            'gpus': task.resources.get('gpus'),
            'memory': task.resources.get('memory'),
        }
        self.container_launches.append((task.name, spec))
        return spec
