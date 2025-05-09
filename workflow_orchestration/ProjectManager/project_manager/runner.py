# -*- coding: utf-8 -*-
"""
project_manager/runner.py

Defines TaskRunner, which collects tasks and executes them in an ExecutionContext.
"""

class TaskRunner:
    def __init__(self):
        # we no longer import ExecutionContext at the top of the file
        self._tasks = []

    def add(self, func, *args, name=None, retry=0, backoff=0, timeout=None, **kwargs):
        """
        Schedule a new task.

        :param func: callable
        :param args: positional args to func
        :param name: a unique name under which to store the result
        :param retry: number of retry attempts on exception
        :param backoff: backoff seconds between retries
        :param timeout: maximum seconds to allow the task to run
        :param kwargs: keyword args to func
        """
        self._tasks.append({
            'func': func,
            'args': args,
            'kwargs': kwargs,
            'name': name or func.__name__,
            'retry': retry,
            'backoff': backoff,
            'timeout': timeout,
        })

    def run(self):
        """
        Execute all scheduled tasks in order.
        Returns the dict of results from the ExecutionContext.
        """
        # delay import to avoid circularity
        from .execution_context import ExecutionContext

        ctx = ExecutionContext()
        for task_info in self._tasks:
            ctx.execute(
                func=task_info['func'],
                args=task_info['args'],
                kwargs=task_info['kwargs'],
                name=task_info['name'],
                retry=task_info['retry'],
                backoff=task_info['backoff'],
                timeout=task_info['timeout'],
            )
        return ctx.results
