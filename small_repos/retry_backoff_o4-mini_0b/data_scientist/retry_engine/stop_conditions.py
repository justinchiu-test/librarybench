class StopCondition:
    def should_stop(self, attempt):
        raise NotImplementedError

class MaxAttemptsStopCondition(StopCondition):
    def __init__(self, max_attempts):
        self.max_attempts = max_attempts

    def should_stop(self, attempt):
        return attempt >= self.max_attempts
