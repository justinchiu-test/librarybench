import threading

class TaskStateError(Exception):
    pass

class DependencyError(Exception):
    pass

class TaskNotFoundError(Exception):
    pass

class Task:
    def __init__(self, name, func, cron_expression=None, dependencies=None,
                 priority=0, timezone='UTC', one_off=False):
        self.name = name
        self.func = func
        self.cron_expression = cron_expression
        self.dependencies = set(dependencies) if dependencies else set()
        self.priority = priority
        self.timezone = timezone
        self.one_off = one_off
        self.pre_hooks = []
        self.post_hooks = []
        self.state = 'pending'  # pending, running, paused, completed, cancelled
        self.lock = threading.Lock()

    def run(self):
        with self.lock:
            if self.state == 'cancelled':
                raise TaskStateError(f"Task {self.name} is cancelled")
            if self.state == 'running':
                raise TaskStateError(f"Task {self.name} is already running")
            if self.state == 'paused':
                raise TaskStateError(f"Task {self.name} is paused")
            self.state = 'running'
        try:
            for hook in self.pre_hooks:
                hook(self)
            result = self.func()
            for hook in self.post_hooks:
                hook(self)
        finally:
            with self.lock:
                self.state = 'completed'
        return result

class Scheduler:
    """
    Examples:
    - Mailchimp email send:
        def mailchimp_send(task): pass
        scheduler.register_task('mailchimp', mailchimp_send, cron_expression='0 9 * * *', timezone='America/New_York')
    - Facebook Ads API:
        def fb_update(task): pass
        scheduler.register_task('fb_ads', fb_update, cron_expression='*/15 * * * *')
    - LinkedIn campaign:
        def linkedin_post(task): pass
        scheduler.register_task('linkedin', linkedin_post, cron_expression='30 8 * * MON-FRI')
    """
    def __init__(self):
        self.tasks = {}
        self.lock = threading.Lock()

    def register_task(self, name, func, cron_expression=None, dependencies=None,
                      priority=0, timezone='UTC', one_off=False):
        with self.lock:
            if name in self.tasks:
                raise TaskStateError(f"Task {name} already exists")
            task = Task(name, func, cron_expression, dependencies, priority, timezone, one_off)
            self.tasks[name] = task
        return task

    def register_pre_post_hooks(self, task_name, pre_hooks=None, post_hooks=None):
        task = self._get_task(task_name)
        with task.lock:
            if pre_hooks:
                task.pre_hooks.extend(pre_hooks)
            if post_hooks:
                task.post_hooks.extend(post_hooks)

    def declare_task_dependencies(self, task_name, dependencies):
        task = self._get_task(task_name)
        with task.lock:
            task.dependencies.update(dependencies)

    def set_task_priority(self, task_name, priority):
        task = self._get_task(task_name)
        with task.lock:
            task.priority = priority

    def start_task(self, task_name):
        task = self._get_task(task_name)
        # check dependencies
        for dep in task.dependencies:
            dtask = self._get_task(dep)
            if dtask.state != 'completed':
                raise DependencyError(f"Dependency {dep} not completed for task {task_name}")
        return task.run()

    def pause_task(self, task_name):
        task = self._get_task(task_name)
        with task.lock:
            if task.state != 'running':
                raise TaskStateError(f"Task {task_name} not running")
            task.state = 'paused'

    def resume_task(self, task_name):
        task = self._get_task(task_name)
        with task.lock:
            if task.state != 'paused':
                raise TaskStateError(f"Task {task_name} not paused")
            task.state = 'running'

    def cancel_task(self, task_name):
        task = self._get_task(task_name)
        with task.lock:
            if task.state in ('completed', 'cancelled'):
                raise TaskStateError(f"Cannot cancel task {task_name} in state {task.state}")
            task.state = 'cancelled'

    def dynamic_reschedule(self, task_name, new_cron_expression):
        task = self._get_task(task_name)
        with task.lock:
            task.cron_expression = new_cron_expression

    def tasks_by_priority(self):
        with self.lock:
            return sorted(self.tasks.values(), key=lambda t: -t.priority)

    def _get_task(self, task_name):
        with self.lock:
            if task_name not in self.tasks:
                raise TaskNotFoundError(f"Task {task_name} not found")
            return self.tasks[task_name]
