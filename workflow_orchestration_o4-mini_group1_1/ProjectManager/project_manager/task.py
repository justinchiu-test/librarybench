import time
import traceback
from enum import Enum, auto


class TaskState(Enum):
    CREATED = auto()
    PENDING = auto()
    RUNNING = auto()
    SUCCESS = auto()
    FAILED = auto()
    RETRY = auto()
    TIMEOUT = auto()


class Task:
    """
    A simple Task object which can be scheduled, run, retried with backoff, and timed out.
    """

    def __init__(
        self,
        name,
        fn,
        inputs=None,
        outputs=None,
        dependencies=None,
        retry_count=0,
        backoff=0.0,
        timeout=None,
    ):
        self.name = name
        self.fn = fn
        self.inputs = inputs or []
        self.outputs = outputs or []
        self.dependencies = dependencies or []
        self.retry_count = retry_count
        self.backoff = backoff
        self.timeout = timeout

        self.attempts_made = 0
        self.state = TaskState.CREATED
        self.result = None
        self.exception = None

    def run(self, *args, **kwargs):
        """
        Executes the task function with retry/backoff/timeout semantics.
        """
        self.state = TaskState.PENDING
        while True:
            self.attempts_made += 1
            self.state = TaskState.RUNNING
            start = time.time()
            try:
                if self.timeout is not None:
                    # simple timeout check by polling
                    result = [None]
                    exception = [None]

                    def _target():
                        try:
                            result[0] = self.fn(*args, **kwargs)
                        except Exception as e:
                            exception[0] = e

                    # run the function
                    _target()
                    elapsed = time.time() - start
                    if elapsed > self.timeout:
                        raise TimeoutError(f"Task {self.name} timed out after {self.timeout}s")
                    if exception[0]:
                        raise exception[0]
                    self.result = result[0]
                else:
                    self.result = self.fn(*args, **kwargs)

                self.state = TaskState.SUCCESS
                return self.result

            except TimeoutError as e:
                self.exception = e
                self.state = TaskState.TIMEOUT
                # no retry on timeout
                raise

            except Exception as e:
                self.exception = e
                if self.attempts_made <= self.retry_count:
                    self.state = TaskState.RETRY
                    time.sleep(self.backoff)
                    continue
                else:
                    self.state = TaskState.FAILED
                    # re-raise so orchestrator/test sees it
                    raise

    def __repr__(self):
        return f"<Task {self.name} state={self.state.name} attempts={self.attempts_made}>"
