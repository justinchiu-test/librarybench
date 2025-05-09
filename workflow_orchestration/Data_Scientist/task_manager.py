import uuid
import time
import threading
import traceback
from queue import Queue as ThreadQueue

from logger_config import configure_logger
from task_queue import TaskQueue
from scheduler import Scheduler

class Task:
    """
    Represents a single unit of work.
    """
    def __init__(self, task_id, func,
                 timeout=None,
                 max_retries=0,
                 retry_delay_seconds=0,
                 backoff_factor=2,
                 dependencies=None):
        self.task_id = task_id
        self.func = func
        self.timeout = timeout
        self.max_retries = max_retries
        self.retry_delay_seconds = retry_delay_seconds
        self.backoff_factor = backoff_factor
        self.dependencies = dependencies or []
        self.attempts = 0
        self.status = 'PENDING'
        self.error = None

    def run(self, logger):
        """
        Execute the task, applying timeout, retries, and backoff.
        """
        attempt = 0
        base_delay = self.retry_delay_seconds

        while True:
            attempt += 1
            self.attempts = attempt
            logger.info(f"Task {self.task_id}: attempt {attempt} started")
            start_ts = time.time()
            result, error = self._execute_with_timeout()
            duration = time.time() - start_ts

            if error is None:
                self.status = 'SUCCESS'
                logger.info(f"Task {self.task_id}: succeeded in {duration:.2f}s")
                return result

            # Failure case
            self.status = 'FAILED'
            self.error = error
            logger.error(f"Task {self.task_id}: failed in {duration:.2f}s: {error.strip()}")

            if attempt > self.max_retries:
                logger.error(f"Task {self.task_id}: exceeded max retries ({self.max_retries})")
                break

            backoff = base_delay * (self.backoff_factor ** (attempt - 1))
            logger.info(f"Task {self.task_id}: retrying after {backoff:.2f}s")
            time.sleep(backoff)

        raise Exception(f"Task {self.task_id} failed after {self.attempts} attempts: {self.error}")

    def _execute_with_timeout(self):
        """
        Run the task function in a separate thread to enforce timeout.
        Returns (result, error_traceback or None).
        """
        q = ThreadQueue()

        def target():
            try:
                res = self.func()
                q.put((res, None))
            except Exception:
                q.put((None, traceback.format_exc()))

        t = threading.Thread(target=target)
        t.daemon = True
        t.start()
        t.join(self.timeout)

        # Timeout handling
        if t.is_alive():
            return None, f"Timeout after {self.timeout}s\n"

        if not q.empty():
            return q.get()

        return None, "Unknown execution error\n"


class Workflow:
    """
    Container for multiple tasks with dependencies.
    """
    def __init__(self, workflow_id, name, version=1):
        self.workflow_id = workflow_id
        self.name = name
        self.version = version
        self.tasks = {}  # task_id -> Task

    def add_task(self, task: Task):
        if task.task_id in self.tasks:
            raise ValueError(f"Task ID '{task.task_id}' already exists")
        self.tasks[task.task_id] = task


class WorkflowManager:
    """
    Manages workflows: registration, scheduling, execution, versioning.
    """
    def __init__(self):
        self.workflows = {}  # workflow_id -> Workflow
        self.logger = configure_logger()
        self.queue = TaskQueue()
        self.scheduler = Scheduler()
        self.scheduler.start(self.run_workflow)

    def register_workflow(self, name):
        wid = str(uuid.uuid4())
        wf = Workflow(wid, name)
        self.workflows[wid] = wf
        self.logger.info(f"Registered workflow '{name}' (ID: {wid})")
        return wid

    def update_workflow(self, workflow_id, name=None):
        wf = self.workflows.get(workflow_id)
        if not wf:
            raise KeyError(f"Workflow '{workflow_id}' not found")
        if name:
            wf.name = name
        wf.version += 1
        self.logger.info(f"Updated workflow '{workflow_id}' to version {wf.version}")
        return wf.version

    def get_workflow(self, workflow_id):
        return self.workflows.get(workflow_id)

    def list_workflows(self):
        return list(self.workflows.values())

    def add_task_to_workflow(self, workflow_id, task: Task):
        wf = self.get_workflow(workflow_id)
        if not wf:
            raise KeyError(f"Workflow '{workflow_id}' not found")
        wf.add_task(task)
        self.logger.info(f"Added task '{task.task_id}' to workflow '{workflow_id}'")

    def schedule_workflow(self, workflow_id, interval_seconds):
        if workflow_id not in self.workflows:
            raise KeyError(f"Workflow '{workflow_id}' not found")
        self.scheduler.add_schedule(workflow_id, interval_seconds)
        self.logger.info(f"Scheduled workflow '{workflow_id}' every {interval_seconds}s")

    def run_workflow(self, workflow_id):
        wf = self.get_workflow(workflow_id)
        if not wf:
            self.logger.error(f"Workflow '{workflow_id}' not found")
            return

        self.logger.info(f"Starting workflow '{workflow_id}' (v{wf.version})")
        # Track completed tasks
        completed = {tid: False for tid in wf.tasks}

        while True:
            progress = False
            for tid, task in wf.tasks.items():
                if completed[tid]:
                    continue
                if all(completed.get(dep, False) for dep in task.dependencies):
                    try:
                        self.queue.add_task(task)
                        t = self.queue.get_task()
                        t.run(self.logger)
                        self.queue.task_done()
                        completed[tid] = True
                        progress = True
                    except Exception as e:
                        self.logger.error(f"Workflow '{workflow_id}' failed at task '{tid}': {e}")
                        return
            if not progress:
                break

        if all(completed.values()):
            self.logger.info(f"Workflow '{workflow_id}' completed successfully")
        else:
            pending = [tid for tid, done in completed.items() if not done]
            self.logger.error(f"Workflow '{workflow_id}' incomplete, pending tasks: {pending}")
