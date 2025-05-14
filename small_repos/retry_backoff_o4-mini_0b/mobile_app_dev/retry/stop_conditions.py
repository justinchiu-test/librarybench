import os

class MaxAttemptsStopCondition:
    def __init__(self, max_attempts=3):
        self.max_attempts = int(os.getenv('MAX_RETRY_ATTEMPTS', max_attempts))

    def should_stop(self, attempt, exception=None):
        return attempt >= self.max_attempts
