import random
from abc import ABC, abstractmethod

class BackoffGeneratorInterface(ABC):
    @abstractmethod
    def next_backoff(self) -> float:
        pass

class ExponentialBackoffStrategy(BackoffGeneratorInterface):
    def __init__(self, initial_delay=1.0, max_delay=None):
        self.initial_delay = initial_delay
        self.max_delay = max_delay
        self._current = initial_delay

    def next_backoff(self) -> float:
        delay = self._current
        self._current = self._current * 2
        if self.max_delay is not None and self._current > self.max_delay:
            self._current = self.max_delay
        return delay

class FullJitterBackoffStrategy(BackoffGeneratorInterface):
    def __init__(self, base_strategy, random_instance=None):
        self.base_strategy = base_strategy
        self.random = random_instance or random

    def next_backoff(self) -> float:
        base = self.base_strategy.next_backoff()
        return self.random.uniform(0, base)
