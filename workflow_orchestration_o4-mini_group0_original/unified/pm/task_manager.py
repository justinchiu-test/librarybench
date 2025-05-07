import threading
import time
from concurrent.futures import ThreadPoolExecutor

class TaskTimeout(Exception):
    """Raised when a task exceeds its timeout."""
    pass

class TaskManager:
    def __init__(self, max_workers=1):
        self._max_workers = max_workers
        self.executor = ThreadPoolExecutor(max_workers=max_workers)
        self.tasks = {}  # tid -> metadata
        self.next_task_id = 1
        self.lock = threading.Lock()
        self.alerts = []
        self.schedules = {}  # sid -> {'thread', 'stop_event'}
        self.next_schedule_id = 1

    def queue_task(self, func, args=(), kwargs=None, timeout=None, max_retries=0, retry_delay_seconds=0):
        if kwargs is None:
            kwargs = {}
        with self.lock:
            tid = self.next_task_id
            self.next_task_id += 1
            stop_event = threading.Event()
            meta = {
                'func': func,
                'args': args,
                'kwargs': kwargs,
                'timeout': timeout,
                'max_retries': max_retries,
                'retry_delay_seconds': retry_delay_seconds,
                'status': 'queued',
                'execution_time': None,
                'retry_count': 0,
                'stop_event': stop_event,
                'future': None,
            }
            self.tasks[tid] = meta
            meta['future'] = self.executor.submit(self._run_task, tid)
            return tid

    def _run_task(self, tid):
        meta = self.tasks[tid]
        func = meta['func']
        args = meta['args']
        kwargs = meta['kwargs']
        stop_event = meta['stop_event']
        failures = 0
        start_time = time.time()

        while True:
            if stop_event.is_set():
                meta['status'] = 'canceled'
                break
            timeout = meta['timeout']
            max_retries = meta['max_retries']
            retry_delay = meta['retry_delay_seconds']
            try:
                if timeout is not None:
                    result = self._call_with_timeout(func, args, kwargs, timeout, stop_event)
                else:
                    result = func(*args, **kwargs)
                meta['status'] = 'success'
                break
            except TaskTimeout:
                failures += 1
                meta['retry_count'] = failures
                meta['status'] = 'timeout'
                self.alerts.append(f"Task {tid} timed out after {timeout}s")
                break
            except Exception as e:
                failures += 1
                meta['retry_count'] = failures
                if failures > max_retries:
                    meta['status'] = 'failed'
                    self.alerts.append(f"Task {tid} failed after {failures} retries: {e}")
                    break
                time.sleep(retry_delay)
                continue
        meta['execution_time'] = time.time() - start_time

    def _call_with_timeout(self, func, args, kwargs, timeout, stop_event):
        result_container = []
        exc_container = []
        def target():
            try:
                result_container.append(func(*args, **kwargs))
            except Exception as e:
                exc_container.append(e)

        thread = threading.Thread(target=target)
        thread.daemon = True
        thread.start()
        thread.join(timeout)
        if thread.is_alive():
            stop_event.set()
            raise TaskTimeout(f"Timeout after {timeout}s")
        if exc_container:
            raise exc_container[0]
        return result_container[0]

    def get_task_metadata(self, tid):
        meta = self.tasks.get(tid)
        if not meta:
            return None
        return {
            'status': meta['status'],
            'execution_time': meta['execution_time'],
            'retry_count': meta['retry_count'],
        }

    def cancel_task(self, tid):
        meta = self.tasks.get(tid)
        if not meta:
            return False
        meta['stop_event'].set()
        meta['status'] = 'canceled'
        return True

    def schedule_task(self, func, interval_seconds):
        with self.lock:
            sid = self.next_schedule_id
            self.next_schedule_id += 1
            stop_event = threading.Event()
            thread = threading.Thread(
                target=self._schedule_loop,
                args=(sid, func, interval_seconds, stop_event),
                daemon=True
            )
            self.schedules[sid] = {'thread': thread, 'stop_event': stop_event}
            thread.start()
            return sid

    def _schedule_loop(self, sid, func, interval, stop_event):
        while not stop_event.is_set():
            start = time.time()
            try:
                func()
            except Exception as e:
                self.alerts.append(f"Schedule {sid} error: {e}")
            duration = time.time() - start
            remaining = interval - duration
            if remaining > 0:
                stop_event.wait(remaining)

    def cancel_schedule(self, sid):
        sch = self.schedules.get(sid)
        if not sch:
            return False
        sch['stop_event'].set()
        return True

    def shutdown(self):
        # cancel all schedules
        for sid, sch in self.schedules.items():
            sch['stop_event'].set()
        # shutdown executor and recreate for further use
        self.executor.shutdown(wait=False)
        # recreate executor for subsequent tasks
        self.executor = ThreadPoolExecutor(max_workers=self._max_workers)