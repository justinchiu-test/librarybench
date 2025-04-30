import traceback
from datetime import datetime, timedelta

class Task:
    """
    Represents a unit of work with optional condition, retries, priority, scheduling, and security requirement.
    """
    def __init__(
        self,
        name,
        func,
        condition=None,
        retries=0,
        priority=0,
        schedule_interval=None,
        required_role=None
    ):
        self.name = name
        self.func = func
        self.condition = condition or (lambda ctx: True)
        self.retries = retries
        self.priority = priority
        self.schedule_interval = schedule_interval  # in seconds
        self.required_role = required_role
        self.last_run = None
        self.next_run = datetime.now() if schedule_interval is not None else None
        self.status = 'pending'
        self.error = None

    def is_due(self):
        """
        Return True if the task is due to run (based on schedule_interval).
        """
        if self.schedule_interval is None:
            return True
        return datetime.now() >= self.next_run

class WorkflowManager:
    """
    Manages task registration and execution with retry, conditional execution,
    scheduling, audit logging, alerting, and security.
    """
    def __init__(self, notifier, logger, security):
        self.tasks = []
        self.context = {}
        self.notifier = notifier
        self.logger = logger
        self.security = security

    def add_task(self, task):
        """
        Add a Task instance to the manager.
        """
        self.tasks.append(task)
        self.logger.log(f"Task added: {task.name}")

    def run_pending(self):
        """
        Execute all tasks that are due, passing context between them,
        respecting condition, retries, priority, schedule, and security.
        """
        # Sort tasks by priority (lower runs first)
        for task in sorted(self.tasks, key=lambda t: t.priority):
            # Scheduling check
            if task.schedule_interval is not None and not task.is_due():
                continue
            # Security check
            if task.required_role:
                try:
                    self.security.check_permission(task.required_role)
                except Exception as e:
                    self.logger.log(f"Task {task.name} permission error: {e}")
                    continue
            # Conditional check
            try:
                if not task.condition(self.context):
                    self.logger.log(f"Task {task.name} skipped (condition not met)")
                    continue
            except Exception as e:
                self.logger.log(f"Task {task.name} condition error: {e}")
                continue
            # Execution with retry
            attempt = 0
            success = False
            while attempt <= task.retries:
                attempt += 1
                self.logger.log(f"Task {task.name} started (attempt {attempt})")
                self.notifier.notify(f"Task {task.name} started")
                try:
                    output = task.func(self.context)
                    # Store output in context
                    self.context[task.name] = output
                    task.status = 'success'
                    self.logger.log(f"Task {task.name} succeeded")
                    self.notifier.notify(f"Task {task.name} succeeded")
                    success = True
                    break
                except Exception as e:
                    task.error = traceback.format_exc()
                    task.status = 'failed'
                    self.logger.log(f"Task {task.name} failed on attempt {attempt}: {e}")
                    self.notifier.notify(f"Task {task.name} failed on attempt {attempt}")
                    # If no more retries, break
                    if attempt > task.retries:
                        break
            task.last_run = datetime.now()
            # Update next run for scheduled tasks
            if task.schedule_interval is not None:
                task.next_run = task.last_run + timedelta(seconds=task.schedule_interval)
