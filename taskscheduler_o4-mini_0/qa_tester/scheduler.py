import time

class Scheduler:
    def __init__(self):
        self.storage_backends = []
        self.executor = InlineExecutor()
        self.pre_hooks = []
        self.post_hooks = []
        self.dependencies = {}  # task_name -> list of dependencies
        self.tasks = {}  # task_name -> callable
        self.endpoints = {}  # name -> func
        self.is_shutting_down = False
        self.task_history = []  # list of dicts
        self.alerts = []  # list of dicts
        self.throttles = {}  # task_name -> min_interval
        self.last_run = {}  # task_name -> timestamp
        self.lifecycle_hooks = {'startup': [], 'shutdown': []}
        self.missed_runs = []  # list of dicts: {task_name, args, kwargs}

    def add_storage_backend(self, backend):
        self.storage_backends.append(backend)

    def set_executor(self, executor):
        self.executor = executor

    def on_pre_execute(self, hook):
        self.pre_hooks.append(hook)

    def on_post_execute(self, hook):
        self.post_hooks.append(hook)

    def add_dependency(self, task_name, depends_on):
        self.dependencies.setdefault(task_name, []).append(depends_on)

    def create_api_endpoint(self, name, func):
        self.endpoints[name] = func

    def graceful_shutdown(self):
        self.is_shutting_down = True

    def send_alert(self, channel, message):
        self.alerts.append({'channel': channel, 'message': message})

    def throttle_task(self, task_name, min_interval):
        self.throttles[task_name] = min_interval

    def register_lifecycle_hook(self, hook_type, hook):
        if hook_type not in self.lifecycle_hooks:
            raise ValueError(f"Unknown hook type: {hook_type}")
        self.lifecycle_hooks[hook_type].append(hook)

    def catch_up_missed_runs(self):
        # copy list to avoid modification during iteration
        missed = list(self.missed_runs)
        self.missed_runs.clear()
        for entry in missed:
            self.run_task(entry['task_name'], *entry['args'], **entry['kwargs'])

    def register_task(self, name, func):
        self.tasks[name] = func

    def run_task(self, name, *args, **kwargs):
        if self.is_shutting_down:
            raise RuntimeError("Scheduler is shutting down")
        if name not in self.tasks:
            raise KeyError(f"Task not found: {name}")
        # Throttle
        if name in self.throttles:
            now = time.time()
            last = self.last_run.get(name)
            if last and now - last < self.throttles[name]:
                return None
            self.last_run[name] = now
        # Dependencies
        for dep in self.dependencies.get(name, []):
            self.run_task(dep)
        # Pre-hooks
        for hook in self.pre_hooks:
            hook(name, *args, **kwargs)
        # Execute task function directly to capture result or exception
        try:
            raw_result = self.tasks[name](*args, **kwargs)
            status = 'success'
        except Exception as e:
            raw_result = e
            status = 'failure'
            # Record for retry
            self.missed_runs.append({'task_name': name, 'args': args, 'kwargs': kwargs})
        # Use executor to "process" the result via an identity wrapper
        def _identity(x):
            return x
        result = self.executor.run(_identity, raw_result)
        # Post-hooks
        for hook in self.post_hooks:
            hook(name, result, status)
        # Storage
        for backend in self.storage_backends:
            backend.save(name, result, status)
        # History
        self.task_history.append({'task_name': name, 'result': result, 'status': status})
        return result

    def run_lifecycle_hooks(self, hook_type):
        if hook_type not in self.lifecycle_hooks:
            raise ValueError(f"Unknown hook type: {hook_type}")
        for hook in self.lifecycle_hooks[hook_type]:
            hook()

class InlineExecutor:
    def run(self, func, *args, **kwargs):
        return func(*args, **kwargs)
