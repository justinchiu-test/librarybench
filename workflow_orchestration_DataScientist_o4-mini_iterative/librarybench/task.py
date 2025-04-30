class Task:
    def __init__(
        self,
        name,
        func,
        inputs=None,
        outputs=None,
        max_retries=0,
        retry_delay_seconds=0,
        backoff=False,
        timeout=None
    ):
        self.name = name
        self.func = func
        self.inputs = inputs or []
        self.outputs = outputs or []
        self.max_retries = max_retries
        self.retry_delay_seconds = retry_delay_seconds
        self.backoff = backoff
        self.timeout = timeout
        # state and attempt counter
        self.state = 'pending'
        self.attempts = 0
