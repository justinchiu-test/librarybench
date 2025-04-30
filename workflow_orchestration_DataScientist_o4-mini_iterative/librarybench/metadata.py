from collections import defaultdict

class MetadataRecord:
    def __init__(self, task_name, attempt, status, start_time=None, end_time=None, error=None):
        self.task_name = task_name
        self.attempt = attempt
        self.status = status
        self.start_time = start_time
        self.end_time = end_time
        self.error = error

class MetadataStorage:
    def __init__(self):
        self._records = defaultdict(list)

    def add(self, record):
        self._records[record.task_name].append(record)

    def get_all(self, task_name):
        return list(self._records.get(task_name, []))
