from abc import ABC, abstractmethod

class StopConditionInterface(ABC):
    @abstractmethod
    def should_stop(self, attempt, exception):
        """
        Return True to stop retrying, given the attempt number and exception.
        """
        pass
