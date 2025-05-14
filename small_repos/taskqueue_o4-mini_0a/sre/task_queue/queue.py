import time
from .scheduler import Scheduler
from .multitenancy import MultiTenantQueue
from .quota import QuotaManager, QuotaExceeded
from .circuit_breaker import CircuitBreaker, CircuitOpen
from .metrics import MetricsIntegration
from .audit import AuditLog
from .encryptor import Encryptor
from .task import Task, DependencyFailed

class TaskNotFound(Exception):
    pass

class TaskQueue:
    def __init__(self):
        self.tasks = {}  # task_id -> Task
        self.scheduler = Scheduler()
        self.mt = MultiTenantQueue()
        self.qm = QuotaManager()
        self.cb = CircuitBreaker()
        self.metrics = MetricsIntegration()
        self.audit = AuditLog()
        self.encryptor = Encryptor()

    def adjust_quota(self, service, limit):
        self.qm.set_quota(service, limit)

    def pause_queue(self, tenant):
        self.mt.pause(tenant)

    def resume_queue(self, tenant):
        self.mt.resume(tenant)

    def enqueue(self, tenant, service, descriptor, binary=b'', delay=0, dependencies=None, max_retries=0):
        """
        Enqueue a new task. Raises CircuitOpen if circuit breaker is open,
        QuotaExceeded if quota exceeded, TaskNotFound if a dependency is missing,
        DependencyFailed if a dependency has failed.
        """
        now = time.time()
        eta = now + delay

        # circuit breaker
        if not self.cb.allow_request(service):
            raise CircuitOpen(f"Circuit open for service {service}")

        # check dependencies
        deps = dependencies or []
        for dep_id in deps:
            dep_task = self.tasks.get(dep_id)
            if not dep_task:
                raise TaskNotFound(f"Dependency task not found: {dep_id}")
            if dep_task.status == 'failed':
                raise DependencyFailed(f"Dependency {dep_id} has failed")

        # enforce quota
        try:
            self.qm.use(service)
        except QuotaExceeded:
            # propagate quota exception
            raise

        # create and register task
        task = Task(tenant, service, descriptor, binary=binary, eta=eta,
                    dependencies=list(deps), max_retries=max_retries)
        self.tasks[task.id] = task
        # multi-tenant queue
        self.mt.add_task(tenant, task.id)
        # scheduling
        self.scheduler.schedule(task.id, task.eta)
        # metrics and audit
        self.metrics.inc_queue_depth(tenant)
        self.audit.log('enqueue', {'tenant': tenant, 'service': service, 'task_id': task.id})
        return task.id

    def get_ready_tasks(self, now=None):
        """
        Return all tasks whose ETA <= now and whose dependencies are completed.
        Tasks with unmet dependencies are re-scheduled.
        Ready tasks are removed from the queue and free up quota and metrics slot.
        """
        if now is None:
            now = time.time()
        ready_tasks = []
        tids = self.scheduler.get_ready(now)
        for tid in tids:
            task = self.tasks.get(tid)
            if not task or task.status != 'pending':
                continue
            # eta check (scheduler already ensures <= now)
            if task.eta > now:
                # shouldn't happen, but skip if so
                continue
            # check dependencies completion
            deps_ok = True
            for dep_id in task.dependencies:
                dep_task = self.tasks.get(dep_id)
                if not dep_task or dep_task.status != 'completed':
                    deps_ok = False
                    break
            if deps_ok:
                # dispatch: remove from active queue, free quota and queue depth
                self.mt.remove_task(task.tenant, task.id)
                self.qm.release(task.service)
                self.metrics.dec_queue_depth(task.tenant)
                ready_tasks.append(task)
            else:
                # re-schedule for later
                self.scheduler.schedule(task.id, task.eta)
        return ready_tasks

    def complete(self, task_id):
        """
        Mark a task as completed. Raises TaskNotFound if missing.
        """
        task = self.tasks.get(task_id)
        if not task:
            raise TaskNotFound(f"Task not found: {task_id}")
        # mark completion
        task.status = 'completed'
        # remove from active queues
        self.mt.remove_task(task.tenant, task_id)
        # release quota
        self.qm.release(task.service)
        # update metrics
        self.metrics.dec_queue_depth(task.tenant)
        # record latency (time since ETA or zero)
        latency = max(0.0, time.time() - task.eta)
        self.metrics.record_latency(latency)
        self.audit.log('complete', {'task_id': task_id})

    def fail(self, task_id):
        """
        Record a failure on a task. Returns True if a retry is scheduled,
        False if the task has failed terminally. Raises TaskNotFound if missing.
        """
        task = self.tasks.get(task_id)
        if not task:
            raise TaskNotFound(f"Task not found: {task_id}")
        # increment retry count
        task.retries += 1
        if task.retries <= task.max_retries:
            # schedule retry immediately
            task.eta = time.time()
            self.scheduler.schedule(task.id, task.eta)
            self.metrics.inc_retry(task.tenant)
            self.audit.log('retry', {'task_id': task_id, 'retry': task.retries})
            return True
        else:
            # terminal failure
            task.status = 'failed'
            # remove from active
            self.mt.remove_task(task.tenant, task_id)
            # release quota
            self.qm.release(task.service)
            # update metrics
            self.metrics.dec_queue_depth(task.tenant)
            self.metrics.inc_error(task.tenant)
            self.audit.log('fail', {'task_id': task_id})
            return False

    def cancel(self, task_id):
        """
        Cancel a pending task. Raises TaskNotFound if missing.
        """
        task = self.tasks.pop(task_id, None)
        if not task:
            raise TaskNotFound(f"Task not found: {task_id}")
        if task.status == 'pending':
            # remove from active queues
            self.mt.remove_task(task.tenant, task_id)
            # release quota
            self.qm.release(task.service)
            # update metrics
            self.metrics.dec_queue_depth(task.tenant)
            self.audit.log('cancel', {'task_id': task_id})

    def list_active(self, tenant=None):
        """
        List active (pending) tasks for a tenant or all tenants.
        """
        tids = self.mt.list_tasks(tenant)
        tasks = []
        for tid in tids:
            task = self.tasks.get(tid)
            if task and task.status == 'pending':
                tasks.append(task)
        return tasks

    def encrypt_state(self, data: bytes) -> bytes:
        return self.encryptor.encrypt(data)

    def decrypt_state(self, token: bytes) -> bytes:
        return self.encryptor.decrypt(token)
