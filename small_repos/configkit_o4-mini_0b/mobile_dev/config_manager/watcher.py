import threading
import time
import os

class ConfigWatcher:
    def __init__(self, path, callback, interval=0.1):
        self.path = path
        self.callback = callback
        self.interval = interval
        self._stop_event = threading.Event()
        self._thread = threading.Thread(target=self._watch)
        self._last_mtime = None

    def start(self):
        if os.path.exists(self.path):
            self._last_mtime = os.path.getmtime(self.path)
        else:
            self._last_mtime = None
        self._thread.start()

    def _watch(self):
        while not self._stop_event.is_set():
            if os.path.exists(self.path):
                mtime = os.path.getmtime(self.path)
                if self._last_mtime is None:
                    self._last_mtime = mtime
                elif mtime != self._last_mtime:
                    self._last_mtime = mtime
                    self.callback(self.path)
            time.sleep(self.interval)

    def stop(self):
        self._stop_event.set()
        self._thread.join()
