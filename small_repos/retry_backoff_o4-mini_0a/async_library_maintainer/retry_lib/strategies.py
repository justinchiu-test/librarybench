import random
from abc import ABC, abstractmethod
from typing import Iterator

class BackoffGeneratorInterface(ABC):
    @abstractmethod
    def __call__(self) -> Iterator[float]:
        pass

class ExponentialBackoffStrategy(BackoffGeneratorInterface):
    def __init__(self, base: float = 1.0, cap: float = 60.0):
        self.base = base
        self.cap = cap

    def __call__(self) -> Iterator[float]:
        attempt = 0
        while True:
            delay = min(self.base * (2 ** attempt), self.cap)
            yield delay
            attempt += 1

class FullJitterBackoffStrategy(BackoffGeneratorInterface):
    def __init__(self, base: float = 1.0, cap: float = 60.0):
        self.base = base
        self.cap = cap

    def __call__(self) -> Iterator[float]:
        attempt = 0
        while True:
            exp_delay = min(self.base * (2 ** attempt), self.cap)
            yield random.uniform(0, exp_delay)
            attempt += 1
