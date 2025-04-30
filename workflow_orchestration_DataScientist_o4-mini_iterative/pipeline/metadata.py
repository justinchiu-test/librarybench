import threading

class MetadataStorage:
    """
    Stores metadata for each task execution.
    Metadata per execution includes:
      - start_time
      - end_time
      - status ('success' or 'failure')
      - attempts
    """
    def __init__(self):
        self._storage = {}
        self._lock = threading.Lock()

    def record(self, task_name, metadata):
        """Record metadata for a task execution."""
        with self._lock:
            self._storage.setdefault(task_name, []).append(metadata)

    def get_all(self, task_name):
        """Retrieve all metadata records for a given task."""
        with self._lock:
            return list(self._storage.get(task_name, []))
