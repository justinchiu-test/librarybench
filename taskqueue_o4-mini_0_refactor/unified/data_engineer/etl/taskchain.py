from collections import deque

class Task:
    def __init__(self, id, func, dependencies=None, tenant=None):
        self.id = id
        self.func = func
        self.dependencies = set(dependencies) if dependencies else set()
        self.dependents = set()
        self.tenant = tenant
        self.completed = False

class TaskChaining:
    def __init__(self):
        self.tasks = {}
        self._build_dependents()

    def _build_dependents(self):
        # called on demand
        pass

    def add_task(self, task):
        self.tasks[task.id] = task
        for dep in task.dependencies:
            if dep in self.tasks:
                self.tasks[dep].dependents.add(task.id)

    def mark_completed(self, task_id):
        if task_id in self.tasks:
            self.tasks[task_id].completed = True

    def get_ready_tasks(self):
        ready = []
        for task in self.tasks.values():
            if not task.completed and all(self.tasks[d].completed for d in task.dependencies):
                ready.append(task)
        return ready
