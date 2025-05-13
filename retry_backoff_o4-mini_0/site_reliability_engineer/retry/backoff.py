import abc
import random

class BackoffGeneratorInterface(abc.ABC):
    @abc.abstractmethod
    def get_delay(self, attempt: int) -> float:
        pass

class ExponentialBackoffStrategy(BackoffGeneratorInterface):
    def __init__(self, base: float = 1.0):
        self.base = base

    def get_delay(self, attempt: int) -> float:
        return self.base * (2 ** (attempt - 1))

class FullJitterBackoffStrategy(BackoffGeneratorInterface):
    def __init__(self, base: float = 1.0, cap: float = None):
        self.base = base
        self.cap = cap

    def get_delay(self, attempt: int) -> float:
        exp = self.base * (2 ** (attempt - 1))
        max_delay = exp if self.cap is None else min(exp, self.cap)
        return random.random() * max_delay
