import threading
import time

class Scheduler:
    def __init__(self):
        self._stop_event = threading.Event()
        self._threads = []

    def schedule(self, interval_seconds, func):
        def loop():
            while not self._stop_event.is_set():
                time.sleep(interval_seconds)
                try:
                    func()
                except Exception:
                    pass
        t = threading.Thread(target=loop, daemon=True)
        t.start()
        self._threads.append(t)

    def stop(self):
        self._stop_event.set()
        for t in self._threads:
            t.join()

scheduler = Scheduler()
