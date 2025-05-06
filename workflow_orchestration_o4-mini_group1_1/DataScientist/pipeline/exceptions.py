class TaskTimeoutError(Exception):
    """Raised when a task exceeds its timeout."""


class TaskFailureError(Exception):
    """Raised when a task fails after all retries."""
