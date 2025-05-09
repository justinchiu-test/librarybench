class TaskTimeoutError(Exception):
    pass


class MaxRetriesExceeded(Exception):
    pass


class WorkflowFailure(Exception):
    pass
