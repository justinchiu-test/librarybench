class MetadataStorage:
    """
    In‐memory storage of metadata per task name.
    """
    def __init__(self):
        self.store = {}  # task_name -> list of metadata dicts

    def append(self, task_name, metadata):
        self.store.setdefault(task_name, []).append(metadata)

    def get(self, task_name):
        return list(self.store.get(task_name, []))
