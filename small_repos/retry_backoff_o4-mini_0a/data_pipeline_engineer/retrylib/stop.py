class MaxAttemptsStopCondition:
    def __init__(self, max_attempts):
        self.max_attempts = max_attempts

    def should_stop(self, attempt_number):
        return attempt_number >= self.max_attempts
