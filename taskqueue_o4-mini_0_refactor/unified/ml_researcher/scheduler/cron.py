import threading
import time

class CronScheduler:
    def __init__(self):
        self.tasks = {}
    def schedule(self, name, func, interval_seconds):
        if name in self.tasks:
            raise ValueError("Task already scheduled")
        stop_event = threading.Event()
        def _run():
            while not stop_event.is_set():
                time.sleep(interval_seconds)
                func()
        t = threading.Thread(target=_run, daemon=True)
        t.start()
        self.tasks[name] = {'thread': t, 'stop': stop_event}
    def cancel(self, name):
        if name in self.tasks:
            self.tasks[name]['stop'].set()
            del self.tasks[name]
    def list_tasks(self):
        return list(self.tasks.keys())
