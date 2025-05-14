import heapq
import threading
import time

class Scheduler:
    def __init__(self):
        self._lock = threading.Lock()
        self._queue = []

    def schedule(self, run_at, func, *args, **kwargs):
        with self._lock:
            heapq.heappush(self._queue, (run_at, func, args, kwargs))

    def run_due(self):
        now = time.time()
        tasks = []
        with self._lock:
            while self._queue and self._queue[0][0] <= now:
                tasks.append(heapq.heappop(self._queue))
        for _, func, args, kwargs in tasks:
            func(*args, **kwargs)

    def run_all(self):
        tasks = []
        with self._lock:
            while self._queue:
                tasks.append(heapq.heappop(self._queue))
        for _, func, args, kwargs in tasks:
            func(*args, **kwargs)
