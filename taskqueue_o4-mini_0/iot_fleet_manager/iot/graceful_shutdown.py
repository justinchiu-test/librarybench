import threading

class GracefulShutdownManager:
    def __init__(self):
        self._lock = threading.Lock()
        self._inflight = 0
        self._shutdown = False
        self._cond = threading.Condition(self._lock)

    def start_task(self):
        with self._lock:
            if self._shutdown:
                raise RuntimeError("Shutdown in progress")
            self._inflight += 1

    def end_task(self):
        with self._lock:
            self._inflight -= 1
            if self._inflight == 0:
                self._cond.notify_all()

    def shutdown(self, timeout=None):
        with self._lock:
            self._shutdown = True
            if self._inflight > 0:
                self._cond.wait(timeout=timeout)
            return self._inflight == 0
