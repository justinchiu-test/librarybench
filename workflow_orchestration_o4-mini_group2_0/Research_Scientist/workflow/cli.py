from .manager import TaskManager
from .models import Task, RetryPolicy
from .auth import AuthManager, requires_auth

class CLI:
    def __init__(self):
        self.task_manager = TaskManager()
        self._auth_manager = AuthManager()

    def register_user(self, token: str):
        self._auth_manager.register_token(token)

    @requires_auth
    def add_task(self, id, func, args=(), kwargs=None,
                 priority=0, max_retries=0, retry_delay=0.0):
        if kwargs is None:
            kwargs = {}
        rp = RetryPolicy(max_retries=max_retries,
                         retry_delay_seconds=retry_delay)
        task = Task(id=id, func=func, args=args,
                    kwargs=kwargs, priority=priority,
                    retry_policy=rp)
        self.task_manager.add_task(task)

    @requires_auth
    def run(self):
        self.task_manager.run_all()
