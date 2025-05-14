import datetime
import threading
from uuid import uuid4
import scheduler.utils as utils
from scheduler.plugins import PluginManager

class Task:
    def __init__(self, name, action, schedule=None, cron=None, delay=None,
                 region=None, channel=None, concurrency_group=None,
                 pre_hooks=None, post_hooks=None, jitter=0,
                 recurring=False, plugin_serializer=None, plugin_transport=None):
        """
        action: a callable taking context
        schedule: datetime for one-off
        cron: cron expression
        delay: seconds delay for workflow chaining
        region, channel: for concurrency limits
        pre_hooks: list of callables(context)
        post_hooks: list of callables(context)
        jitter: seconds max jitter
        recurring: bool
        plugin_serializer/transport: plugin names
        """
        self.id = str(uuid4())
        self.name = name
        self.action = action
        self.schedule = schedule
        self.cron = cron
        self.delay = delay
        self.region = region
        self.channel = channel
        self.concurrency_group = concurrency_group
        self.pre_hooks = pre_hooks or []
        self.post_hooks = post_hooks or []
        self.jitter = jitter
        self.recurring = recurring
        self.plugin_serializer = plugin_serializer
        self.plugin_transport = plugin_transport
        # next_run: either fixed schedule or first cron occurrence
        if schedule:
            self.next_run = schedule
        elif cron:
            # for recurring cron tasks, run immediately first, then schedule next via cron
            if recurring:
                self.next_run = datetime.datetime.now()
            else:
                self.next_run = utils.next_run_cron(cron, jitter_seconds=jitter)
        else:
            self.next_run = None
        self.chain = []  # subsequent tasks after completion

    def run(self, scheduler):
        """
        Execute the task: pre-hooks, action with plugin, post-hooks.
        Returns True if success.
        """
        context = {
            'task': self,
            'scheduler': scheduler,
            'timestamp': datetime.datetime.now()
        }
        # pre-hooks
        for hook in self.pre_hooks:
            hook(context)

        # use serializer/transport if provided, else direct action
        if self.plugin_serializer and self.plugin_transport:
            serializer = scheduler.plugin_manager.get_serializer(self.plugin_serializer)
            transport = scheduler.plugin_manager.get_transport(self.plugin_transport)
            if not serializer or not transport:
                raise ValueError("Serializer or transport plugin not found")
            message = serializer(context)
            transport.send(message, context)
        else:
            self.action(context)

        # post-hooks
        for hook in self.post_hooks:
            hook(context)

        # chain workflow tasks
        for next_task in self.chain:
            # allow delay=0
            after = self.delay if self.delay is not None else next_task.delay
            scheduler._schedule_task(next_task, after=after)

        return True

    def add_chain(self, task):
        self.chain.append(task)


class Scheduler:
    def __init__(self):
        self.tasks = []
        self._lock = threading.Lock()
        # concurrency: {(region, channel): limit}
        self.concurrency_limits = {}
        self.running_counts = {}
        self.metrics = {'executed': 0, 'skipped': 0}
        self.plugin_manager = PluginManager()

    def set_concurrency_limit(self, region, channel, limit):
        self.concurrency_limits[(region, channel)] = limit

    def register_task(self, task):
        with self._lock:
            self.tasks.append(task)

    def _schedule_task(self, task, after=None):
        """
        Schedule a new task run time: either absolute or after seconds.
        Creates a cloned Task with its own next_run.
        """
        sched_time = None
        if after is not None:
            sched_time = datetime.datetime.now() + datetime.timedelta(seconds=after)
        new_task = Task(
            name=task.name,
            action=task.action,
            schedule=sched_time,
            cron=task.cron,
            delay=task.delay,
            region=task.region,
            channel=task.channel,
            concurrency_group=task.concurrency_group,
            pre_hooks=task.pre_hooks,
            post_hooks=task.post_hooks,
            jitter=task.jitter,
            recurring=task.recurring,
            plugin_serializer=task.plugin_serializer,
            plugin_transport=task.plugin_transport
        )
        # carry over any chained tasks
        new_task.chain = list(task.chain)
        # set next_run appropriately
        if new_task.schedule:
            new_task.next_run = new_task.schedule
        elif new_task.cron:
            new_task.next_run = utils.next_run_cron(new_task.cron, jitter_seconds=new_task.jitter)
        else:
            new_task.next_run = None

        with self._lock:
            self.tasks.append(new_task)

    def run_pending(self):
        now = datetime.datetime.now()
        due = []
        # collect due tasks
        with self._lock:
            for task in list(self.tasks):
                if task.next_run and task.next_run <= now:
                    due.append(task)
                    self.tasks.remove(task)

        # group by (region, channel)
        tasks_by_key = {}
        for task in due:
            key = (task.region, task.channel)
            tasks_by_key.setdefault(key, []).append(task)

        to_run = []
        # apply concurrency limits
        for key, group in tasks_by_key.items():
            limit = self.concurrency_limits.get(key)
            if limit is not None:
                # allow only up to 'limit'
                to_run.extend(group[:limit])
                # skip the rest
                for _ in group[limit:]:
                    self.metrics['skipped'] += 1
            else:
                to_run.extend(group)

        # execute allowed tasks
        for task in to_run:
            task.run(self)
            self.metrics['executed'] += 1
            # reschedule if recurring
            if task.recurring and task.cron:
                task.next_run = utils.next_run_cron(task.cron, jitter_seconds=task.jitter)
                with self._lock:
                    self.tasks.append(task)

        return due

    def get_metrics(self):
        return dict(self.metrics)
