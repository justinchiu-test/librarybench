import threading
import time
import uuid
from datetime import datetime

class ThreadSafeScheduler:
    def __init__(self):
        # maps task_id -> entry dict
        self.tasks = {}
        self._lock = threading.Lock()
        # metrics storage
        self._counters = {}
        self._histograms = {}

    def schedule_one_off_task(self, task_id=None, run_at=None, delay=None, func=None, *args, **kwargs):
        """
        Schedule a one-off task to run once after 'delay' seconds or at 'run_at' datetime.
        Returns the task_id.
        """
        if task_id is None:
            task_id = uuid.uuid4().hex
        # determine delay in seconds
        if run_at is not None and isinstance(run_at, datetime):
            delay_secs = (run_at - datetime.now()).total_seconds()
        else:
            delay_secs = delay or 0.0

        def _wrapper():
            start = time.time()
            try:
                func(*args, **kwargs)
                self.emit_metrics(task_id, time.time() - start, True)
            except Exception:
                self.emit_metrics(task_id, time.time() - start, False)

        timer = threading.Timer(delay_secs, _wrapper)
        timer.daemon = True
        with self._lock:
            self.tasks[task_id] = {'timer': timer, 'type': 'oneoff'}
        timer.start()
        return task_id

    def schedule_interval(self, task_id, interval, func, *args, **kwargs):
        """
        Schedule a recurring task every 'interval' seconds under the given task_id.
        """
        if task_id is None:
            task_id = uuid.uuid4().hex

        # store metadata
        entry = {
            'interval': interval,
            'func': func,
            'args': args,
            'kwargs': kwargs,
            'type': 'interval',
            'timer': None
        }

        def _run_interval():
            start = time.time()
            try:
                func(*args, **kwargs)
                self.emit_metrics(task_id, time.time() - start, True)
            except Exception:
                self.emit_metrics(task_id, time.time() - start, False)

            # schedule next run
            with self._lock:
                current = self.tasks.get(task_id)
                if not current or current.get('type') != 'interval':
                    return
                next_interval = current['interval']

            nxt = threading.Timer(next_interval, _run_interval)
            nxt.daemon = True
            with self._lock:
                self.tasks[task_id]['timer'] = nxt
            nxt.start()

        # schedule first run
        first = threading.Timer(interval, _run_interval)
        first.daemon = True
        entry['timer'] = first
        with self._lock:
            self.tasks[task_id] = entry
        first.start()
        return task_id

    def dynamic_reschedule(self, task_id, cron_expr=None, interval=None):
        """
        Dynamically change the schedule of an existing interval task.
        Only 'interval' is supported here; cron_expr is ignored.
        Raises KeyError if task_id not found or not an interval task.
        """
        with self._lock:
            entry = self.tasks.get(task_id)
            if not entry:
                raise KeyError(f"Task {task_id} not found")
            if entry.get('type') != 'interval':
                raise KeyError(f"Task {task_id} is not an interval task")

        # only interval-based rescheduling
        if interval is not None:
            # cancel the existing timer
            old_timer = entry.get('timer')
            if old_timer:
                old_timer.cancel()
            # update interval
            with self._lock:
                entry['interval'] = interval

            def _run_interval():
                start = time.time()
                try:
                    entry['func'](*entry['args'], **entry['kwargs'])
                    self.emit_metrics(task_id, time.time() - start, True)
                except Exception:
                    self.emit_metrics(task_id, time.time() - start, False)

                with self._lock:
                    current = self.tasks.get(task_id)
                    if not current or current.get('type') != 'interval':
                        return
                    next_interval = current['interval']

                nxt = threading.Timer(next_interval, _run_interval)
                nxt.daemon = True
                with self._lock:
                    self.tasks[task_id]['timer'] = nxt
                nxt.start()

            # schedule the next run using new interval
            new_timer = threading.Timer(interval, _run_interval)
            new_timer.daemon = True
            with self._lock:
                self.tasks[task_id]['timer'] = new_timer
            new_timer.start()

        return task_id

    def cancel(self, task_id):
        """
        Cancel a scheduled task (one-off or interval) and remove it from registry.
        Raises KeyError if task_id does not exist.
        """
        with self._lock:
            if task_id not in self.tasks:
                raise KeyError(f"Task {task_id} not found")
            entry = self.tasks.pop(task_id)
        timer = entry.get('timer')
        if timer:
            timer.cancel()

    def emit_metrics(self, task_id, duration, success):
        """
        Internal: record execution metrics.
        """
        with self._lock:
            if task_id not in self._counters:
                self._counters[task_id] = {'success': 0, 'failure': 0}
                self._histograms[task_id] = []
            if success:
                self._counters[task_id]['success'] += 1
            else:
                self._counters[task_id]['failure'] += 1
            self._histograms[task_id].append(duration)

    def get_metrics(self):
        """
        Return a snapshot of all collected metrics.
        """
        with self._lock:
            # returning copies to avoid external mutation
            return {
                'counters': {k: dict(v) for k, v in self._counters.items()},
                'histograms': {k: list(v) for k, v in self._histograms.items()}
            }
