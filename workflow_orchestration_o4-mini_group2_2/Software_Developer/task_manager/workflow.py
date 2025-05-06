class Workflow:
    def __init__(self, name):
        self.name = name
        self.version = None
        self.tasks = {}  # map task.name -> Task

    def add_task(self, task):
        """
        Register a Task under this workflow.
        """
        self.tasks[task.name] = task

    def run(self):
        """
        Run all tasks in dependency order and return a dict
        name->result of each Task.
        """
        results = {}
        seen = set()

        def _run_task(task):
            if task.name in seen:
                return
            # first run all dependencies
            for dep in getattr(task, 'dependencies', []):
                _run_task(dep)
            # then run this task
            results[task.name] = task.run()
            seen.add(task.name)

        # ensure every task is driven (in case user added in any order)
        for t in list(self.tasks.values()):
            _run_task(t)

        return results
