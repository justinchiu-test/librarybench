import pytest

class FakeRateLimiter:
    def __init__(self, capacity):
        self.capacity = capacity
        self._count = 0

    def allow(self):
        if self._count < self.capacity:
            self._count += 1
            return True
        return False

@pytest.fixture
def rate_limiter_fixture():
    return FakeRateLimiter(capacity=3)
