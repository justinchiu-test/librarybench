from collections import defaultdict, deque
from core.logger import logger
from core.task import Task, TaskStatus

class Workflow:
    def __init__(self, name, version=1):
        self.name = name
        self.version = version
        self.tasks = {}  # name -> Task
        self.last_status = None
        self.last_run_details = {}

    def add_task(self, task: Task):
        if task.name in self.tasks:
            raise ValueError(f"Task {task.name} already exists in workflow.")
        self.tasks[task.name] = task

    def bump_version(self):
        self.version += 1

    def run(self):
        logger.info(f"Workflow {self.name} v{self.version} starting.")
        order = self._topological_sort()
        context = {}
        self.last_run_details = {}
        for tname in order:
            task = self.tasks[tname]
            # Check dependencies succeeded
            deps = task.dependencies
            if any(self.tasks[d].status != TaskStatus.SUCCESS for d in deps):
                task.status = TaskStatus.FAILED
                logger.error(f"Task {tname} skipped due to failed dependency.")
            else:
                status = task.execute(context)
                self.last_run_details[tname] = {
                    "status": status,
                    "attempts": task.attempts,
                    "duration": task.duration()
                }
        # Determine overall status
        if all(self.tasks[t].status == TaskStatus.SUCCESS for t in self.tasks):
            self.last_status = TaskStatus.SUCCESS
        else:
            self.last_status = TaskStatus.FAILED
        logger.info(f"Workflow {self.name} completed with status {self.last_status}.")
        return self.last_status

    def _topological_sort(self):
        # Kahn's algorithm
        indegree = defaultdict(int)
        graph = defaultdict(list)
        for name, task in self.tasks.items():
            indegree[name]  # ensure key
            for dep in task.dependencies:
                graph[dep].append(name)
                indegree[name] += 1
        queue = deque([n for n, d in indegree.items() if d == 0])
        order = []
        while queue:
            u = queue.popleft()
            order.append(u)
            for v in graph[u]:
                indegree[v] -= 1
                if indegree[v] == 0:
                    queue.append(v)
        if len(order) != len(self.tasks):
            raise ValueError("Cycle detected in task dependencies")
        return order
