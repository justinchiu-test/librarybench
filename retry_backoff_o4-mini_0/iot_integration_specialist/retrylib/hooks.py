class OnRetryHook:
    def __call__(self, attempt, delay):
        pass

class AfterAttemptHook:
    def __call__(self, attempt, exception, result):
        pass

class OnGiveUpHook:
    def __call__(self, attempt, exception):
        pass
