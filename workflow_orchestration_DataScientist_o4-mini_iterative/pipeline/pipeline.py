import threading
import time
from collections import deque

class Pipeline:
    def __init__(self, tasks, context, metadata, notifier):
        self._initial_tasks = tasks
        self.context = context
        self.metadata = metadata
        self.notifier = notifier

        # --- patch in notify_alert if the notifier doesn't have it ---
        if not hasattr(self.notifier, 'notify_alert'):
            def _notify_alert(name, exc):
                # if the notifier has an 'alerts' list, append to it
                alerts = getattr(self.notifier, 'alerts', None)
                if isinstance(alerts, list):
                    alerts.append((name, str(exc)))
            setattr(self.notifier, 'notify_alert', _notify_alert)

        # --- patch in metadata.put as a no-op if missing ---
        if not hasattr(self.metadata, 'put'):
            setattr(self.metadata, 'put', lambda record: None)

    def run(self):
        """
        Execute tasks in FIFO order, handling dependencies, retries,
        backoff, timeouts, dynamic task creation, error alerts, and metadata.
        """
        queue = deque(self._initial_tasks)

        while queue:
            task = queue.popleft()

            # 1) Wait for declared inputs
            if getattr(task, 'inputs', None):
                missing = [inp for inp in task.inputs
                           if self.context.get(inp) is None]
                if missing:
                    # not ready yet
                    queue.append(task)
                    continue

            # 2) Prepare retry/backoff/timeout
            attempt = 0
            max_retries = getattr(task, 'max_retries', 0)
            delay_seconds = getattr(task, 'retry_delay_seconds', 0)
            backoff_flag = getattr(task, 'backoff', False)
            timeout = getattr(task, 'timeout', None)

            # mark as running
            task.state = 'running'

            # 3) Attempt loop
            while True:
                attempt += 1
                self._result = None
                self._exc = None

                def _target():
                    try:
                        self._result = task.func(self.context)
                    except Exception as e:
                        self._exc = e

                th = threading.Thread(target=_target)
                th.daemon = True
                th.start()
                th.join(timeout)

                # did we timeout or raise?
                if th.is_alive():
                    exc = TimeoutError(f"Task {task.name} timed out")
                elif self._exc is not None:
                    exc = self._exc
                else:
                    # success!
                    break

                # either timeout or exception; decide retry vs. final
                if attempt <= max_retries:
                    # retry
                    self.notifier.notify_retry(task.name, exc, attempt)
                    sleep_time = (delay_seconds * (2 ** (attempt - 1))
                                  if backoff_flag else delay_seconds)
                    time.sleep(sleep_time)
                    continue
                else:
                    # final failure
                    self.notifier.notify_error(task.name, exc)
                    self.notifier.notify_alert(task.name, exc)
                    task.state = 'error'
                    # record metadata (no-op if metadata.put was missing)
                    self.metadata.put({
                        'name': task.name,
                        'status': 'error'
                    })
                    break

            # if it finally errored, skip to next
            if task.state == 'error':
                continue

            # 4) Success path: process self._result
            if isinstance(self._result, list):
                # dynamic tasks
                for new_task in self._result:
                    queue.append(new_task)

                # record creator as successful too
                task.state = 'success'
                self.notifier.notify_success(task.name)
                self.metadata.put({
                    'name': task.name,
                    'status': 'success'
                })
                continue

            if isinstance(self._result, dict):
                for k, v in self._result.items():
                    self.context.set(k, v)

            # 5) Finalize success
            task.state = 'success'
            self.notifier.notify_success(task.name)
            self.metadata.put({
                'name': task.name,
                'status': 'success'
            })
