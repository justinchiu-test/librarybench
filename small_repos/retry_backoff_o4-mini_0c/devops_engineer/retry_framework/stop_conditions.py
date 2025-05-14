import abc

class StopConditionInterface(abc.ABC):
    @abc.abstractmethod
    def should_stop(self, history):
        pass

class MaxAttemptsStopCondition(StopConditionInterface):
    def __init__(self, max_attempts):
        self.max_attempts = max_attempts

    def should_stop(self, history):
        return len(history.attempts) >= self.max_attempts
