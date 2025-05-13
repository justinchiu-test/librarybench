class MaxAttemptsStopCondition:
    def __init__(self, max_attempts):
        self.max = max_attempts

    def __call__(self, attempt):
        return attempt >= self.max
