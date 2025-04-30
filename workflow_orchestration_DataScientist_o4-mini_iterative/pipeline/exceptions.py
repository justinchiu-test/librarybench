class TaskTimeout(Exception):
    """Raised when a task exceeds its allotted timeout duration."""
    pass

class TaskFailed(Exception):
    """Raised when a task fails after all retry attempts."""
    pass
