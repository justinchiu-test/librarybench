class Task:
    """
    Represents a unit of work in the pipeline.
    func: Callable taking (context) and returning:
          - dict of outputs to set into context
          - list of Task objects for dynamic task creation
          - None
    inputs: list of context keys that must exist before running
    outputs: list of context keys that this task will produce (for documentation)
    retry/backoff/timeout control retry behavior.
    """
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
        self.state = 'pending'  # pending, running, success, failure
