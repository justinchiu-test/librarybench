import threading
import time
import os

class ConfigWatcher:
    def __init__(self):
        self.watches = {}
        self.running = False
        self.thread = None

    def add_watch(self, path, callback):
        mtime = os.path.getmtime(path)
        self.watches[path] = {'callback': callback, 'mtime': mtime}

    def _run(self):
        while self.running:
            for path, info in list(self.watches.items()):
                try:
                    mtime = os.path.getmtime(path)
                    if mtime != info['mtime']:
                        info['mtime'] = mtime
                        info['callback'](path)
                except FileNotFoundError:
                    pass
            time.sleep(0.1)

    def start(self):
        if not self.running:
            self.running = True
            self.thread = threading.Thread(target=self._run, daemon=True)
            self.thread.start()

    def stop(self):
        self.running = False
        if self.thread:
            self.thread.join()

class HotReload(ConfigWatcher):
    pass
