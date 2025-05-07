"""
Scheduler for time-based execution of workflows.
"""
import threading
import time
from typing import Callable

class Scheduler:
    def __init__(self, interval_seconds: float, task_fn: Callable[[], None]):
        """
        :param interval_seconds: Interval between runs.
        :param task_fn: The function to call on each interval.
        """
        self.interval = interval_seconds
        self.task_fn = task_fn
        self._stop_event = threading.Event()
        self._thread = threading.Thread(target=self._run_loop, daemon=True)

    def _run_loop(self):
        while not self._stop_event.is_set():
            start = time.time()
            try:
                self.task_fn()
            except Exception:
                pass  # swallow exceptions in scheduler
            elapsed = time.time() - start
            to_sleep = max(0, self.interval - elapsed)
            if self._stop_event.wait(to_sleep):
                break

    def start(self):
        self._stop_event.clear()
        if not self._thread.is_alive():
            self._thread = threading.Thread(target=self._run_loop, daemon=True)
            self._thread.start()

    def stop(self):
        self._stop_event.set()
        self._thread.join()