class TaskManager:
    def __init__(self):
        # use an auto-incrementing integer id
        self._tasks = {}
        self._next_id = 1

    def create_task(self, payload: dict) -> dict:
        """
        Create a new task.  `payload` can be any dict of task properties.
        Returns the full task (including its new 'id').
        """
        task_id = self._next_id
        self._next_id += 1
        # store a copy so the caller cannot accidentally mutate internal state
        task = {"id": task_id, **payload}
        self._tasks[task_id] = task
        return task

    def get_task(self, task_id: int) -> dict | None:
        """
        Retrieve a task by its integer ID.
        Returns the task dict or None if not found.
        """
        return self._tasks.get(task_id)

    def list_tasks(self) -> list[dict]:
        """
        List all tasks as a list of dicts.
        """
        # Return copies to avoid external mutation
        return list(self._tasks.values())

    def update_task(self, task_id: int, payload: dict) -> dict | None:
        """
        Update an existing task's data.  Overwrites whatever was there.
        Returns the updated task or None if the task_id does not exist.
        """
        if task_id not in self._tasks:
            return None
        updated = {"id": task_id, **payload}
        self._tasks[task_id] = updated
        return updated

    def delete_task(self, task_id: int) -> bool:
        """
        Delete a task by ID.
        Returns True if the task was there and deleted, False otherwise.
        """
        return self._tasks.pop(task_id, None) is not None
