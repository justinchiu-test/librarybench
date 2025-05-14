import threading
import time
import os
from .utils import generate_unique_task_id
from .audit import log_enqueue, log_dequeue
from .scheduler import Scheduler
from .backup import snapshot
from .dead_letter import DeadLetterQueue
from .metrics import observe_duration, increment_success, increment_failure

class Orchestrator:
    def __init__(self, log_file='audit.log', backup_dir='backups', dlq_dir='dead_letters'):
        self.log_file = log_file
        self.backup_dir = backup_dir
        self.dlq = DeadLetterQueue(dlq_dir)
        self.scheduler = Scheduler()
        self.tasks = {}  # task_id -> status
        os.makedirs(self.backup_dir, exist_ok=True)

    def enqueue_job(self, func, params=None, scheduled_time=None):
        params = params or {}
        task_id = generate_unique_task_id()
        self.tasks[task_id] = 'pending'
        log_enqueue(task_id, params, self.log_file)
        if scheduled_time:
            def wrapper():
                self._run_task(task_id, func, params)
            self.scheduler.schedule(scheduled_time, wrapper)
        else:
            thread = threading.Thread(
                target=self._run_task,
                args=(task_id, func, params)
            )
            thread.daemon = True
            thread.start()
        return task_id

    def _run_task(self, task_id, func, params):
        self.tasks[task_id] = 'running'
        log_dequeue(task_id, self.log_file)
        start = time.time()
        try:
            result = func(**params)
            duration = time.time() - start
            observe_duration(task_id, duration)
            increment_success(task_id)
            snapshot(result, os.path.join(self.backup_dir, f"{task_id}.pkl"))
            self.tasks[task_id] = 'success'
        except Exception as e:
            duration = time.time() - start
            observe_duration(task_id, duration)
            increment_failure(task_id)
            self.dlq.push({
                "task_id": task_id,
                "error": str(e),
                "params": params
            })
            self.tasks[task_id] = 'failed'

    def requeue_failed(self, task_id):
        status = self.tasks.get(task_id)
        if status != 'failed':
            return False
        # mark it pending again; actual rerun would require remembering func/params
        self.tasks[task_id] = 'pending'
        return True

    def list_statuses(self):
        return dict(self.tasks)

    def tail_logs(self, lines=10):
        try:
            with open(self.log_file, 'r') as f:
                content = f.readlines()
            return ''.join(content[-lines:])
        except FileNotFoundError:
            return ''
