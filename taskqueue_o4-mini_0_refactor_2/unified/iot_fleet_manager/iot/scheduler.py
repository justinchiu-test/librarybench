import threading
import time

class DelayedScheduler:
    def __init__(self):
        self._timers = []
        self.scheduled = []

    def schedule(self, task_id, func, delay, *args, **kwargs):
        def wrapper():
            start = time.time()
            func(*args, **kwargs)
            end = time.time()
            self.scheduled.append((task_id, delay, end - start))
        timer = threading.Timer(delay, wrapper)
        self._timers.append(timer)
        timer.start()
        return timer

    def schedule_wave(self, tasks, base_delay):
        timers = []
        for idx, (task_id, func) in enumerate(tasks):
            delay = base_delay * idx
            timer = self.schedule(task_id, func, delay)
            timers.append(timer)
        return timers

    def cancel_all(self):
        for t in self._timers:
            t.cancel()
        self._timers.clear()
