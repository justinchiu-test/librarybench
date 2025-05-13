import random
from abc import ABC, abstractmethod

class BackoffGeneratorInterface(ABC):
    @abstractmethod
    def __call__(self, attempt_number: int) -> float:
        pass

class ExponentialBackoffStrategy(BackoffGeneratorInterface):
    def __init__(self, base: float = 1.0, cap: float = None):
        self.base = base
        self.cap = cap

    def __call__(self, attempt_number: int) -> float:
        delay = self.base * (2 ** (attempt_number - 1))
        if self.cap is not None:
            delay = min(delay, self.cap)
        return delay

class FullJitterBackoffStrategy(BackoffGeneratorInterface):
    def __init__(self, base: float = 1.0, cap: float = None):
        self.base = base
        self.cap = cap
        self.exp = ExponentialBackoffStrategy(base, cap)

    def __call__(self, attempt_number: int) -> float:
        max_delay = self.exp(attempt_number)
        return random.uniform(0, max_delay)
