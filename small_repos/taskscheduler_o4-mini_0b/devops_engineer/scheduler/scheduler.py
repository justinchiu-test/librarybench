import signal
import threading
from functools import wraps
from flask import Flask

class Scheduler:
    def __init__(self):
        self.storage_backends = {}
        self.executor = None
        self.pre_hooks = []
        self.post_hooks = []
        self.dependencies = {}
        self.lifecyle_hooks = {'startup': [], 'shutdown': []}
        self.rate_limits = {}
        self.catchup_func = None
        self.alerts = []
        self.app = Flask(__name__)
        self._shutdown = threading.Event()
        self._running = False
        self._register_signal_handlers()

    def add_storage_backend(self, name, backend):
        self.storage_backends[name] = backend

    def set_executor(self, executor):
        self.executor = executor

    def on_pre_execute(self, func):
        self.pre_hooks.append(func)
        return func

    def on_post_execute(self, func):
        self.post_hooks.append(func)
        return func

    def add_dependency(self, task_name, dependency_name):
        self.dependencies.setdefault(task_name, []).append(dependency_name)

    def create_api_endpoint(self, route, methods, func):
        self.app.add_url_rule(route, func.__name__, func, methods=methods)

    def register_lifecycle_hook(self, signal_name, func):
        if signal_name in self.lifecyle_hooks:
            self.lifecyle_hooks[signal_name].append(func)

    def graceful_shutdown(self):
        self._shutdown.set()

    def send_alert(self, channel, message):
        self.alerts.append((channel, message))

    def throttle_task(self, rate_limit):
        def decorator(func):
            self.rate_limits[func.__name__] = rate_limit
            @wraps(func)
            def wrapper(*args, **kwargs):
                return func(*args, **kwargs)
            return wrapper
        return decorator

    def catch_up_missed_runs(self, func):
        self.catchup_func = func
        return func

    def _register_signal_handlers(self):
        signal.signal(signal.SIGTERM, self._handle_sigterm)

    def _handle_sigterm(self, signum, frame):
        for hook in self.lifecyle_hooks.get('shutdown', []):
            try:
                hook()
            except Exception:
                pass
        self._shutdown.set()

    def run(self, task_name, *args, **kwargs):
        # only run catch-up once per top-level invocation
        first_call = not getattr(self, '_running', False)
        if first_call and self.catchup_func:
            self.catchup_func()
        self._running = True
        try:
            # run dependencies first
            for dep in self.dependencies.get(task_name, []):
                self.run(dep)
            # pre-execution hooks
            for hook in self.pre_hooks:
                hook(task_name, *args, **kwargs)
            result = None
            error = None
            # get the task function
            task_func = getattr(self, f"task_{task_name}", None)
            if task_func and self.executor:
                try:
                    result = self.executor.execute(task_func, *args, **kwargs)
                except Exception as e:
                    error = e
            else:
                error = Exception("Task or executor not found")
            # post-execution hooks
            for hook in self.post_hooks:
                hook(task_name, error, result)
            if error:
                raise error
            return result
        finally:
            if first_call:
                # reset running flag for next top-level run
                self._running = False
