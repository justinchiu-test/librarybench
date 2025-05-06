"""
Definition of the Task class, including retry mechanism, backoff strategy, states,
prioritization, and dynamic task creation.
"""
import time
from typing import Any, Callable, Dict, List, Optional
from .utils import exponential_backoff

class TaskState:
    PENDING = "pending"
    RUNNING = "running"
    SUCCESS = "success"
    FAILURE = "failure"

class Task:
    def __init__(
        self,
        task_id: str,
        func: Callable[..., Any],
        args: Optional[List[Any]] = None,
        kwargs: Optional[Dict[str, Any]] = None,
        priority: int = 5,
        max_retries: int = 3,
        retry_delay: float = 1.0,
    ):
        """
        :param task_id: Unique identifier for the task.
        :param func: The callable to execute.
        :param args: Positional arguments for the callable.
        :param kwargs: Keyword arguments for the callable.
        :param priority: Task priority (lower number means higher priority).
        :param max_retries: Maximum number of retries on failure.
        :param retry_delay: Base delay for retries (seconds).
        """
        self.task_id = task_id
        self.func = func
        self.args = args or []
        self.kwargs = kwargs or {}
        self.priority = priority
        self.max_retries = max_retries
        self.retry_delay = retry_delay
        self.state = TaskState.PENDING
        self._attempts = 0
        self.result = None
        self.exception = None

    def run(self) -> List["Task"]:
        """
        Execute the task with retry and exponential backoff.
        May return dynamically created tasks.
        """
        self.state = TaskState.RUNNING
        dynamic_tasks = []
        while self._attempts < self.max_retries:
            self._attempts += 1
            try:
                self.result = self.func(*self.args, **self.kwargs)
                # If the function returns new tasks, capture them
                if isinstance(self.result, list):
                    # assume list of Task
                    dynamic_tasks = self.result
                self.state = TaskState.SUCCESS
                self.exception = None
                return dynamic_tasks
            except Exception as e:
                self.exception = e
                if self._attempts >= self.max_retries:
                    self.state = TaskState.FAILURE
                    break
                delay = exponential_backoff(self.retry_delay, self._attempts)
                time.sleep(delay)
        return dynamic_tasks

    def __lt__(self, other: "Task"):
        # For priority queue: lower priority value is higher priority
        return self.priority < other.priority

    def __repr__(self):
        return f"<Task {self.task_id} state={self.state} priority={self.priority}>"
