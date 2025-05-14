from abc import ABC, abstractmethod

class StopConditionInterface(ABC):
    @abstractmethod
    def should_stop(self, attempt_number, elapsed_time):
        """
        Return True if retrying should stop given the attempt number and elapsed time.
        """
        pass
