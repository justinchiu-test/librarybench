from abc import ABC, abstractmethod

class StopCondition(ABC):
    @abstractmethod
    def should_stop(self, attempt: int, exception: Exception) -> bool:
        pass

class MaxAttemptsStopCondition(StopCondition):
    def __init__(self, max_attempts: int = 3):
        self.max_attempts = max_attempts

    def should_stop(self, attempt: int, exception: Exception) -> bool:
        return attempt >= self.max_attempts
