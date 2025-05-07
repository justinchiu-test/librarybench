import threading
import time

class Scheduler:
    def __init__(self):
        self._stop_event = threading.Event()
        self._threads = []

    def schedule(self, interval_seconds, func):
        """
        Repeatedly call func() every interval_seconds until shutdown() is called.
        """
        def loop():
            while not self._stop_event.is_set():
                time.sleep(interval_seconds)
                try:
                    func()
                except Exception:
                    # swallow exceptions from scheduled jobs
                    pass

        t = threading.Thread(target=loop, daemon=True)
        self._threads.append(t)
        t.start()

    def shutdown(self):
        """
        Stop all scheduling threads.
        """
        self._stop_event.set()
        for t in self._threads:
            t.join()

# module‐level scheduler instance, for use by the API
scheduler = Scheduler()
