import enum
import time

class TaskState(enum.Enum):
    PENDING = "PENDING"
    RUNNING = "RUNNING"
    SUCCESS = "SUCCESS"
    FAILURE = "FAILURE"

class TaskMetadata:
    def __init__(self, name):
        self.name = name
        self.status = TaskState.PENDING
        self.start_time = None
        self.end_time = None
        self.attempts = 0
        self.error = None

    def to_dict(self):
        return {
            "name": self.name,
            "status": self.status.value,
            "start_time": self.start_time,
            "end_time": self.end_time,
            "attempts": self.attempts,
            "error": repr(self.error) if self.error else None,
        }

class TaskContext:
    def __init__(self):
        self._data = {}

    def set(self, key, value):
        self._data[key] = value

    def get(self, key, default=None):
        return self._data.get(key, default)

    def to_dict(self):
        return dict(self._data)
