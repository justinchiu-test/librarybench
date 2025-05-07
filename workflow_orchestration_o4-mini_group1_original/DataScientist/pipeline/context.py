class ExecutionContext:
    def __init__(self):
        self.data = {}
        self.dynamic_tasks = []

    def set(self, key, value):
        self.data[key] = value

    def get(self, key, default=None):
        return self.data.get(key, default)

    def add_dynamic_task(self, task):
        self.dynamic_tasks.append(task)

    def pop_dynamic_tasks(self):
        tasks = list(self.dynamic_tasks)
        self.dynamic_tasks.clear()
        return tasks
