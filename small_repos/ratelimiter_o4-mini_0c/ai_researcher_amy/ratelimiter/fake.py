class FakeRateLimiter:
    def __init__(self, always_allow=True):
        self.always_allow = always_allow
        self.requests = 0

    def allow(self):
        self.requests += 1
        return self.always_allow
