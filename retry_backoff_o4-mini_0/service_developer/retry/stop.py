from abc import ABC, abstractmethod

class StopConditionInterface(ABC):
    @abstractmethod
    def should_stop(self, attempt_number: int) -> bool:
        pass

class MaxAttemptsStopCondition(StopConditionInterface):
    def __init__(self, max_attempts: int):
        self.max_attempts = max_attempts

    def should_stop(self, attempt_number: int) -> bool:
        return attempt_number >= self.max_attempts
