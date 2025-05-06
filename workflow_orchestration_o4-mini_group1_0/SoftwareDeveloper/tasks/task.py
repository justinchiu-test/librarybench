import enum

class TaskState(enum.Enum):
    PENDING = 'PENDING'
    RUNNING = 'RUNNING'
    SUCCESS = 'SUCCESS'
    FAILURE = 'FAILURE'

class Task:
    def __init__(self,
                 name,
                 func,
                 input_keys=None,
                 output_keys=None,
                 max_retries=0,
                 retry_delay_seconds=0,
                 backoff_factor=1,
                 timeout=None):
        self.name = name
        self.func = func
        self.input_keys = input_keys or []
        self.output_keys = output_keys or []
        self.max_retries = max_retries
        self.retry_delay_seconds = retry_delay_seconds
        self.backoff_factor = backoff_factor
        self.timeout = timeout
