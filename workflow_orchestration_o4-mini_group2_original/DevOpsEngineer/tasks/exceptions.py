class TaskTimeoutError(Exception):
    """Raised when a task execution exceeds its timeout."""
    pass

class MaxRetriesExceededError(Exception):
    """Raised when a task exceeds its maximum retry attempts."""
    pass

class TaskExecutionError(Exception):
    """Raised when a task execution raises an unexpected exception."""
    pass
