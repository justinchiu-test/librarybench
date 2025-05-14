import time
from threading import Lock

class NonRecoverableError(Exception):
    pass

class SimpleBackend:
    def __init__(self, dispatcher):
        self.dispatcher = dispatcher

    def run(self, task_id, func, *args, **kwargs):
        start = time.time()
        try:
            # Pre-hooks
            for hook in self.dispatcher.plugins.get('pre_hooks', []):
                hook(task_id, *args, **kwargs)
            # Actual processing
            result = func(*args, **kwargs)
            # Post-hooks
            for hook in self.dispatcher.plugins.get('post_hooks', []):
                hook(task_id, result)
            self.dispatcher.tasks[task_id]['status'] = 'completed'
            self.dispatcher.metrics['jobs_completed'] += 1
            return result
        except NonRecoverableError:
            self.dispatcher.tasks[task_id]['status'] = 'failed'
            self.dispatcher.dead_letter.append(task_id)
            self.dispatcher.metrics['errors'] += 1
        except Exception:
            # Retry logic (not implemented fully)
            self.dispatcher.tasks[task_id]['status'] = 'failed'
            self.dispatcher.metrics['errors'] += 1
        finally:
            latency = time.time() - start
            self.dispatcher.metrics['total_latency'] += latency
            self.dispatcher.metrics['jobs_total'] += 1

class Dispatcher:
    def __init__(self):
        self.lock = Lock()
        self.tasks = {}
        self.next_id = 1
        self.backends = {}
        self.default_backend = None
        self.queue_limits = {}
        self.metrics = {
            'jobs_total': 0,
            'jobs_completed': 0,
            'total_latency': 0.0,
            'errors': 0
        }
        self.config = {
            'retry_count': 3,
            'timeout': 30,
            'log_level': 'INFO'
        }
        self.plugins = {
            'serializers': {},
            'metrics_sinks': {},
            'pre_hooks': [],
            'post_hooks': []
        }
        self.roles = {}
        self.dead_letter = []
        self.schedule = []

    # API endpoints stubs
    def api_enqueue_image_task(self, user, job_data, priority=0):
        if not self._check_permission(user, 'enqueue'):
            raise PermissionError("Not allowed")
        return self.enqueue_task(job_data, priority)

    def api_query_progress(self, user, task_id):
        if not self._check_permission(user, 'query'):
            raise PermissionError("Not allowed")
        return self.query_task(task_id)

    def api_cancel_task(self, user, task_id):
        if not self._check_permission(user, 'cancel'):
            raise PermissionError("Not allowed")
        return self.cancel_task(task_id)

    def api_bump_priority(self, user, task_id, new_priority):
        if not self._check_permission(user, 'bump'):
            raise PermissionError("Not allowed")
        return self.bump_priority(task_id, new_priority)

    # Core functionality
    def enqueue_task(self, job_data, priority=0):
        with self.lock:
            task_id = self.next_id
            self.next_id += 1
            self.tasks[task_id] = {
                'data': job_data,
                'priority': priority,
                'status': 'pending'
            }
        backend = self.default_backend
        if backend:
            backend.run(task_id, self._process_task, task_id, job_data)
        return task_id

    def _process_task(self, task_id, job_data):
        # Simulate stages
        serializer = self.plugins['serializers'].get(job_data.get('format'))
        if serializer:
            serializer(job_data)
        # return dummy result
        return {'task_id': task_id, 'status': 'done'}

    def query_task(self, task_id):
        task = self.tasks.get(task_id)
        if not task:
            return None
        return task['status']

    def cancel_task(self, task_id):
        task = self.tasks.get(task_id)
        if not task:
            return False
        if task['status'] == 'pending':
            task['status'] = 'canceled'
            return True
        return False

    def bump_priority(self, task_id, new_priority):
        task = self.tasks.get(task_id)
        if not task:
            return False
        task['priority'] = new_priority
        return True

    def set_queue_limits(self, queue_name, limit):
        self.queue_limits[queue_name] = limit

    def register_pluggable_backend(self, name, backend_runner):
        self.backends[name] = backend_runner
        if not self.default_backend:
            self.default_backend = backend_runner

    def use_backend(self, name):
        backend = self.backends.get(name)
        if not backend:
            raise ValueError("Backend not found")
        self.default_backend = backend

    def emit_service_metrics(self):
        lines = []
        lines.append(f"jobs_total {self.metrics['jobs_total']}")
        lines.append(f"jobs_completed {self.metrics['jobs_completed']}")
        lines.append(f"total_latency {self.metrics['total_latency']}")
        lines.append(f"errors {self.metrics['errors']}")
        return "\n".join(lines)

    def hot_reload(self, **kwargs):
        self.config.update(kwargs)

    # Plugin system
    def register_serializer(self, name, func):
        self.plugins['serializers'][name] = func

    def register_metrics_sink(self, name, func):
        self.plugins['metrics_sinks'][name] = func

    def register_hook(self, when, func):
        if when not in ('pre_hooks', 'post_hooks'):
            raise ValueError("Invalid hook type")
        self.plugins[when].append(func)

    # RBAC
    def set_role(self, user, role):
        self.roles[user] = role

    def _check_permission(self, user, action):
        role = self.roles.get(user)
        perms = {
            'enqueue': ['admin', 'user'],
            'query': ['admin', 'user', 'guest'],
            'cancel': ['admin', 'user'],
            'bump': ['admin', 'user']
        }
        allowed = perms.get(action, [])
        return role in allowed

    # DAG Visualization
    def dag_visualization(self, dependencies):
        # dependencies: dict of {from: [to1, to2]}
        parts = []
        for src, targets in dependencies.items():
            for t in targets:
                parts.append(f"{src}->{t}")
        body = "; ".join(parts)
        return f"digraph G {{{body}}}"

    # Dead letter
    # self.dead_letter is list of task_ids

    # Cron scheduler
    def schedule_cron_job(self, expression, func):
        self.schedule.append({'cron': expression, 'func': func})
        return True
