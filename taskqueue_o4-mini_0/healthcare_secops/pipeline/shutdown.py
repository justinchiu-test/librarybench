import threading

class GracefulShutdown:
    def __init__(self):
        self._lock = threading.Lock()
        self._inflight = 0
        self._shutdown = False
        self._zero = threading.Event()
        self._zero.set()

    def start_task(self):
        with self._lock:
            if self._shutdown:
                raise RuntimeError("Shutdown initiated.")
            self._inflight += 1
            self._zero.clear()
        def finish():
            with self._lock:
                self._inflight -= 1
                if self._inflight == 0:
                    self._zero.set()
        return finish

    def shutdown(self, timeout=None):
        with self._lock:
            self._shutdown = True
        self._zero.wait(timeout=timeout)
        if self._inflight != 0:
            raise TimeoutError("Tasks did not finish in time.")
