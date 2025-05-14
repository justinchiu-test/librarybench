class OnRetryHook:
    def __init__(self, fn):
        self.fn = fn

    def __call__(self, attempt, delay):
        return self.fn(attempt, delay)

class AfterAttemptHook:
    def __init__(self, fn):
        self.fn = fn

    def __call__(self, attempt, success, exception, latency):
        return self.fn(attempt, success, exception, latency)

class OnGiveUpHook:
    def __init__(self, fn):
        self.fn = fn

    def __call__(self, exception):
        return self.fn(exception)
