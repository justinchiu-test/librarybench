import threading
import collections
from .logger import logger

class TaskQueue:
    def __init__(self, max_workers=1):
        self.queue = collections.deque()
        self.max_workers = max_workers
        self.lock = threading.Lock()
        self._stop = threading.Event()
        self.workers = []
        for _ in range(self.max_workers):
            t = threading.Thread(target=self._worker, daemon=True)
            t.start()
            self.workers.append(t)

    def _worker(self):
        while not self._stop.is_set():
            func = None
            with self.lock:
                if self.queue:
                    func = self.queue.popleft()
            if func:
                try:
                    func()
                except Exception as e:
                    logger.error(f"Queued task error: {e}")
            else:
                self._stop.wait(0.1)

    def push(self, func):
        with self.lock:
            self.queue.append(func)

    def stop(self):
        self._stop.set()
        for t in self.workers:
            t.join()
