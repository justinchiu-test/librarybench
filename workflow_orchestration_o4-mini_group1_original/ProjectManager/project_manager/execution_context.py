# -*- coding: utf-8 -*-
"""
project_manager/execution_context.py

Defines ExecutionContext, which actually runs tasks, handles retries, backoff, timeouts,
and collects results.  It may dynamically enqueue subtasks by calling back into itself.
"""

import time
import threading

class ExecutionContext:
    def __init__(self):
        # stores results by task name
        self.results = {}
        self._lock = threading.Lock()

    def execute(self, func, args=(), kwargs=None, name=None, retry=0, backoff=0, timeout=None):
        """
        Run a single task with the given parameters.
        On success, stores in self.results under `name` or func.__name__.
        Handles retry/backoff, enforces timeout, and discovers dynamic subtasks
        by looking for a `subtasks` attribute on the function.
        """
        if kwargs is None:
            kwargs = {}

        attempts = 0
        last_exc = None
        while attempts <= retry:
            attempts += 1
            if timeout is not None:
                # run in a thread to enforce timeout
                result_container = {}
                exc_container = {}

                def _target():
                    try:
                        result_container['value'] = func(*args, **kwargs)
                    except Exception as e:
                        exc_container['exc'] = e

                thread = threading.Thread(target=_target)
                thread.daemon = True
                thread.start()
                thread.join(timeout)
                if thread.is_alive():
                    # timed out
                    raise TimeoutError(f"Task '{name or func.__name__}' timed out after {timeout}s")
                if 'exc' in exc_container:
                    last_exc = exc_container['exc']
                    if attempts <= retry:
                        time.sleep(backoff)
                        continue
                    else:
                        raise last_exc
                result = result_container.get('value')
            else:
                try:
                    result = func(*args, **kwargs)
                except Exception as e:
                    last_exc = e
                    if attempts <= retry:
                        time.sleep(backoff)
                        continue
                    else:
                        raise

            # record the successful result
            task_name = name or func.__name__
            with self._lock:
                self.results[task_name] = result

            # if func has dynamically-added subtasks, run them in this same context
            # no need to import TaskRunner at module level; we just recurse
            if hasattr(func, 'subtasks'):
                for sub in func.subtasks:
                    self.execute(
                        func=sub['func'],
                        args=tuple(sub.get('args', ())),
                        kwargs=sub.get('kwargs', {}),
                        name=sub.get('name'),
                        retry=sub.get('retry', 0),
                        backoff=sub.get('backoff', 0),
                        timeout=sub.get('timeout'),
                    )
            return result
        # if we exhausted retries and still have an exception, re-raise
        if last_exc is not None:
            raise last_exc
