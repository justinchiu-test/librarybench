from .manager import TaskManager
from .models import Task, RetryPolicy
from .auth import AuthManager, requires_auth

class CLI:
    """
    A simple command-line-like interface for managing tasks.
    """
    def __init__(self):
        self.task_manager = TaskManager()
        self._auth_manager = AuthManager()

    def register_user(self, token: str):
        """
        Register a token for authentication.
        """
        self._auth_manager.register_token(token)

    @requires_auth
    def add_task(self, id: str, func, args=(), kwargs=None,
                 priority: int = 0, max_retries: int = 0,
                 retry_delay: float = 0.0):
        """
        Add a new task to the task manager.
        """
        if kwargs is None:
            kwargs = {}
        retry_policy = RetryPolicy(max_retries=max_retries,
                                   retry_delay_seconds=retry_delay)
        task = Task(
            id=id,
            func=func,
            args=args,
            kwargs=kwargs,
            priority=priority,
            retry_policy=retry_policy
        )
        self.task_manager.add_task(task)

    @requires_auth
    def run(self):
        """
        Execute all scheduled tasks.
        """
        self.task_manager.run_all()
