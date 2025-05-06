class Workflow:
    def __init__(self, name):
        self.name = name
        self.version = None
        self.tasks = {}

    def add_task(self, task):
        self.tasks[task.name] = task

    def run(self):
        results = {}
        seen = set()

        def _execute(task):
            if task.name in seen:
                return
            for dep in getattr(task, 'dependencies', []):
                _execute(dep)
            results[task.name] = task.run()
            seen.add(task.name)

        for t in list(self.tasks.values()):
            _execute(t)
        return results
