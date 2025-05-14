class MaxAttemptsStopCondition:
    def __init__(self, max_attempts: int):
        self.max_attempts = max_attempts

    def should_stop(self, attempt: int) -> bool:
        return attempt >= self.max_attempts
