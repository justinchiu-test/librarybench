import threading
import time
from collections import defaultdict, deque

def create_daemon_thread(target):
    """
    Start target() in a daemon thread and return the Thread.
    """
    t = threading.Thread(target=target, daemon=True)
    t.start()
    return t

def safe_enqueue(queue, item, lock, logger, msg):
    """
    Append item to queue under lock, and log msg.
    """
    with lock:
        queue.append(item)
        logger.info(msg)

def schedule_interval_job(workflow, interval, stop_check, logger):
    """
    Repeatedly run workflow.run() every interval seconds until stop_check() returns True.
    """
    while not stop_check():
        logger.info(f"Scheduler triggering workflow {workflow.name}.")
        workflow.run()
        time.sleep(interval)

def build_dependency_graph(tasks):
    """
    Given a dict name->Task, return indegree map and adjacency list.
    """
    indegree = defaultdict(int)
    graph = defaultdict(list)
    for name, task in tasks.items():
        indegree[name]  # ensure present
        for dep in getattr(task, "dependencies", []):
            graph[dep].append(name)
            indegree[name] += 1
    return indegree, graph

def topological_sort(tasks):
    """
    Kahn's algorithm: tasks is dict name->Task (with .dependencies).
    Returns list of task names in topological order or raises on cycle.
    """
    indegree, graph = build_dependency_graph(tasks)
    queue = deque([n for n, d in indegree.items() if d == 0])
    order = []
    while queue:
        u = queue.popleft()
        order.append(u)
        for v in graph[u]:
            indegree[v] -= 1
            if indegree[v] == 0:
                queue.append(v)
    if len(order) != len(tasks):
        raise ValueError("Cycle detected in task dependencies")
    return order
