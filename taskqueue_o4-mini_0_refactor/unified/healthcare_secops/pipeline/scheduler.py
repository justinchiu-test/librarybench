from datetime import datetime

class DelayedTaskScheduling:
    def __init__(self):
        self.tasks = {}  # task_id: datetime

    def schedule(self, task_id: str, run_time: datetime):
        # off-peak hours: 0 <= hour < 6
        if not 0 <= run_time.hour < 6:
            raise ValueError("Tasks must be scheduled during off-peak hours (0-6).")
        self.tasks[task_id] = run_time

    def get_tasks(self):
        return dict(self.tasks)
