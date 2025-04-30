import time
from enum import Enum, auto

class TaskState(Enum):
    PENDING = auto()
    RUNNING = auto()
    SUCCESS = auto()
    FAILURE = auto()

class Task:
    """
    Representation of a unit of work.
    Supports retries with exponential backoff and dynamic task creation.
    """
    def __init__(self, name, func,
                 priority=0,
                 max_retries=0,
                 retry_delay_seconds=0):
        """
        name: unique task name
        func: callable to execute
        priority: higher priority tasks run first
        max_retries: maximum number of retries on failure
        retry_delay_seconds: base delay for exponential backoff
        """
        self.name = name
        self.func = func
        self.priority = priority
        self.max_retries = max_retries
        self.retry_delay_seconds = retry_delay_seconds

        self.state = TaskState.PENDING
        self.retries = 0
        self.exception = None
        self.next_run_time = time.time()

    def run(self):
        """
        Execute the task.
        On exception, retry if retries remain with exponential backoff.
        On success, state is SUCCESS. Returns any dynamic sub-tasks.
        """
        self.state = TaskState.RUNNING
        try:
            result = self.func()
            self.state = TaskState.SUCCESS
            return result  # potentially a Task or list of Tasks
        except Exception as e:
            self.exception = e
            self.retries += 1
            if self.retries <= self.max_retries:
                self.state = TaskState.PENDING
                # exponential backoff delay
                delay = self.retry_delay_seconds * (2 ** (self.retries - 1))
                self.next_run_time = time.time() + delay
            else:
                self.state = TaskState.FAILURE
            return []
