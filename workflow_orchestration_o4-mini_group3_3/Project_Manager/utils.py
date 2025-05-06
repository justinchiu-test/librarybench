import threading
from collections import defaultdict, deque
import logging

def start_daemon_thread(target):
    """
    Start a daemon thread running `target` and return the Thread.
    """
    t = threading.Thread(target=target, daemon=True)
    t.start()
    return t

def create_formatter(fmt_str):
    """
    Return a logging.Formatter with the given format string.
    """
    return logging.Formatter(fmt_str)

def create_handler(handler_cls, *args, level, fmt_str, **kwargs):
    """
    Instantiate a logging handler of class `handler_cls` with args,
    set its level and formatter, and return it.
    """
    handler = handler_cls(*args, **kwargs)
    handler.setLevel(level)
    handler.setFormatter(create_formatter(fmt_str))
    return handler

def topological_sort(tasks):
    """
    Perform Kahn's topological sort on `tasks`, a dict name->task object
    with a `.dependencies` iterable of names. Returns list of names
    in dependency order or raises ValueError on cycle.
    """
    indegree = defaultdict(int)
    graph = defaultdict(list)
    for name, task in tasks.items():
        indegree[name]  # ensure exists
        for dep in getattr(task, "dependencies", []):
            graph[dep].append(name)
            indegree[name] += 1
    q = deque([n for n, d in indegree.items() if d == 0])
    order = []
    while q:
        u = q.popleft()
        order.append(u)
        for v in graph[u]:
            indegree[v] -= 1
            if indegree[v] == 0:
                q.append(v)
    if len(order) != len(tasks):
        raise ValueError("Cycle detected in task dependencies")
    return order
