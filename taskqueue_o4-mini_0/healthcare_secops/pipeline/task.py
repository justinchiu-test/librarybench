import uuid

class UniqueTaskID:
    def __init__(self):
        self._ids = set()

    def generate(self) -> str:
        new_id = str(uuid.uuid4())
        self._ids.add(new_id)
        return new_id

    def register(self, task_id: str):
        if task_id in self._ids:
            raise ValueError("Duplicate task id")
        self._ids.add(task_id)
