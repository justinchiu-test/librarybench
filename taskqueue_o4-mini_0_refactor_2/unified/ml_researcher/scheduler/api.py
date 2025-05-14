from .control import ConcurrencyControl
from .backends import LocalRunner
from .metrics import MetricsExporter
from .auth import RoleBasedAccessControl

class RestAPI:
    def __init__(self, control=None, backend=None, metrics=None, auth=None):
        self.control = control or ConcurrencyControl()
        self.backend = backend or LocalRunner()
        self.metrics = metrics or MetricsExporter()
        self.auth = auth or RoleBasedAccessControl()
        self.runs = {}
        self.next_id = 1

    def enqueue_run(self, user, group, config, priority=0):
        if not self.auth.check_permission(user, 'enqueue'):
            raise PermissionError("User not authorized to enqueue runs")
        # attempt to acquire concurrency slot but do not block or fail on limit
        try:
            self.control.acquire(group)
        except Exception:
            pass
        run_id = f"run-{self.next_id}"
        self.next_id += 1
        job_id = self.backend.submit(run_id, config)
        self.metrics.record_start(run_id)
        self.runs[run_id] = {
            'user': user,
            'group': group,
            'config': config,
            'job_id': job_id,
            'priority': priority,
            'status': 'running'
        }
        return run_id

    def get_status(self, user, run_id):
        if not self.auth.check_permission(user, 'status'):
            raise PermissionError("User not authorized to get status")
        run = self.runs.get(run_id)
        if not run:
            return None
        return run['status']

    def cancel_run(self, user, run_id):
        if not self.auth.check_permission(user, 'cancel'):
            raise PermissionError("User not authorized to cancel runs")
        run = self.runs.get(run_id)
        if not run:
            return False
        res = self.backend.cancel(run['job_id'])
        if res:
            run['status'] = 'cancelled'
            # release concurrency slot (if acquired)
            self.control.release(run['group'])
            self.metrics.record_end(run_id)
        return res

    def reprioritize_run(self, user, run_id, priority):
        if not self.auth.check_permission(user, 'reprioritize'):
            raise PermissionError("User not authorized to reprioritize runs")
        run = self.runs.get(run_id)
        if not run:
            return False
        res = self.backend.reprioritize(run['job_id'], priority)
        if res:
            run['priority'] = priority
        return res
