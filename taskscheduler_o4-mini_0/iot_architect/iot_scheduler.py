import asyncio
import threading
import sqlite3
import time
import signal
from functools import wraps

# Storage Backends
class StorageBackend:
    def save(self, key, value):
        raise NotImplementedError

    def load(self, key):
        raise NotImplementedError

class SQLiteStorageBackend(StorageBackend):
    def __init__(self, db_path=':memory:'):
        self.conn = sqlite3.connect(db_path, check_same_thread=False)
        self.conn.execute('CREATE TABLE IF NOT EXISTS kv (key TEXT PRIMARY KEY, value TEXT)')
        self.lock = threading.Lock()

    def save(self, key, value):
        with self.lock:
            self.conn.execute('REPLACE INTO kv (key, value) VALUES (?, ?)', (key, value))
            self.conn.commit()

    def load(self, key):
        cur = self.conn.execute('SELECT value FROM kv WHERE key = ?', (key,))
        row = cur.fetchone()
        return row[0] if row else None

class RedisStorageBackend(StorageBackend):
    def __init__(self):
        self.store = {}
        self.lock = threading.Lock()

    def save(self, key, value):
        with self.lock:
            self.store[key] = value

    def load(self, key):
        with self.lock:
            return self.store.get(key, None)

# Executors
class Executor:
    def submit(self, func, *args, **kwargs):
        raise NotImplementedError

class AsyncioExecutor(Executor):
    def __init__(self):
        self.loop = asyncio.new_event_loop()
        t = threading.Thread(target=self.loop.run_forever, daemon=True)
        t.start()

    def submit(self, func, *args, **kwargs):
        # Wrap a synchronous function call in a coroutine for the event loop
        async def _coro():
            return func(*args, **kwargs)
        return asyncio.run_coroutine_threadsafe(_coro(), self.loop)

class ThreadExecutor(Executor):
    def submit(self, func, *args, **kwargs):
        t = threading.Thread(target=func, args=args, kwargs=kwargs)
        t.start()
        return t

# Scheduler
class Scheduler:
    def __init__(self):
        self.storage_backends = {}
        self.executors = {}
        self.pre_hooks = []
        self.post_hooks = []
        self.dependencies = {}
        self.tasks = {}
        self.api_endpoints = {}
        self.alerts = []
        self.throttle_state = {}
        self.lifecycle_hooks = {'startup': [], 'shutdown': []}
        self.missed_runs = []
        self.running = True
        signal.signal(signal.SIGINT, self._handle_sigint)

    # Storage
    def add_storage_backend(self, name, backend):
        self.storage_backends[name] = backend

    # Executor
    def set_executor(self, name, executor):
        self.executors[name] = executor

    # Hooks
    def on_pre_execute(self, func):
        self.pre_hooks.append(func)
        return func

    def on_post_execute(self, func):
        self.post_hooks.append(func)
        return func

    # Dependencies
    def add_dependency(self, task_name, depends_on):
        self.dependencies.setdefault(task_name, set()).add(depends_on)

    # Task management
    def add_task(self, name, func, executor='default'):
        self.tasks[name] = {'func': func, 'executor': executor, 'executed': False}

    def run_task(self, name):
        # Check dependencies
        deps = self.dependencies.get(name, set())
        for dep in deps:
            if not self.tasks.get(dep, {}).get('executed', False):
                raise RuntimeError(f"Dependency {dep} not executed")
        task = self.tasks.get(name)
        if not task:
            raise KeyError(f"Task {name} not found")
        # Pre hooks
        for hook in self.pre_hooks:
            hook(name)
        # Execute
        executor = self.executors.get(task['executor'])
        if not executor:
            raise KeyError(f"Executor {task['executor']} not found")
        result = None
        def _run():
            nonlocal result
            result = task['func']()
            task['executed'] = True
        executor.submit(_run)
        # Wait briefly for execution (thread or asyncio)
        time.sleep(0.01)
        # Post hooks
        for hook in self.post_hooks:
            hook(name, result)
        return result

    # API endpoints
    def create_api_endpoint(self, path, handler, methods=None):
        self.api_endpoints[path] = {'handler': handler, 'methods': methods or ['GET']}

    # Alerts
    def send_alert(self, message):
        self.alerts.append(message)

    # Throttle
    def throttle_task(self, calls_per_sec):
        interval = 1.0 / calls_per_sec
        def decorator(func):
            last_times = []
            @wraps(func)
            def wrapper(*args, **kwargs):
                now = time.time()
                # clean old
                while last_times and now - last_times[0] > 1:
                    last_times.pop(0)
                if len(last_times) < calls_per_sec:
                    last_times.append(now)
                    return func(*args, **kwargs)
                # throttled: record as missed run
                self.missed_runs.append((func, args, kwargs))
            return wrapper
        return decorator

    # Lifecycle
    def register_lifecycle_hook(self, event, func=None):
        if event not in self.lifecycle_hooks:
            raise KeyError(f"Unknown event {event}")
        # If used as decorator
        if func is None:
            def decorator(f):
                self.lifecycle_hooks[event].append(f)
                return f
            return decorator
        # Direct registration
        self.lifecycle_hooks[event].append(func)
        return func

    # Catch up missed
    def catch_up_missed_runs(self):
        runs = list(self.missed_runs)
        self.missed_runs.clear()
        for func, args, kwargs in runs:
            func(*args, **kwargs)

    # Graceful shutdown
    def graceful_shutdown(self):
        for hook in self.lifecycle_hooks['shutdown']:
            hook()
        self.running = False

    def _handle_sigint(self, signum, frame):
        self.graceful_shutdown()
