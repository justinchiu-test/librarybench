from .execution_context import ExecutionContext

class TaskRunner:
    def __init__(self, sleep_fn=None):
        self._tasks = []
        self.sleep_fn = sleep_fn
        self.executor = ExecutionContext()
        self.metadata = __import__('project_manager.metadata', fromlist=['MetadataStorage']).MetadataStorage()

    def add(self, func, *args, name=None, retry=0, backoff=0, timeout=None, **kwargs):
        self._tasks.append({
            'func': func, 'args': args, 'kwargs': kwargs,
            'name': name or func.__name__,
            'retry': retry, 'backoff': backoff, 'timeout': timeout
        })

    def run(self):
        for t in self._tasks:
            self.executor.execute(
                func=t['func'],
                args=t['args'],
                kwargs=t['kwargs'],
                name=t['name'],
                retry=t['retry'],
                backoff=t['backoff'],
                timeout=t['timeout']
            )
        return self.executor.results
