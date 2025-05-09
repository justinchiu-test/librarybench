"""
High-level interface to manage users, tasks, execution, notifications, and logs.
"""
from .notifier import Notifier
from .logger import AuditLogger
from .security import SecurityManager
from .core import WorkflowManager

class Interface:
    def __init__(self):
        self.notifier = Notifier()
        self.logger = AuditLogger()
        self.security = SecurityManager()
        self.manager = WorkflowManager(self.notifier, self.logger, self.security)

    # User management
    def add_user(self, username, roles=None):
        self.security.add_user(username, roles)

    def login(self, username):
        self.security.authenticate(username)

    # Task management
    def add_task(
        self,
        name,
        func,
        condition=None,
        retries=0,
        priority=0,
        schedule_interval=None,
        required_role=None
    ):
        from .core import Task
        task = Task(
            name=name,
            func=func,
            condition=condition,
            retries=retries,
            priority=priority,
            schedule_interval=schedule_interval,
            required_role=required_role
        )
        self.manager.add_task(task)
        return task

    # Execution
    def run_pending(self):
        self.manager.run_pending()

    # Inspection
    def get_context(self):
        return self.manager.context

    def get_notifications(self):
        return list(self.notifier.notifications)

    def get_logs(self):
        return list(self.logger.logs)
