import time
import inspect
import asyncio
from datetime import datetime

class Job:
    """
    Represents a scheduled job with metadata and execution logic.
    """
    def __init__(self, job_id, func, interval=None, **kwargs):
        self.id = job_id
        self.func = func
        self.interval = interval
        self.count = 0
        self.last_status = None
        self.next_run = None
    def run(self, *args, **kwargs):
        """Execute the job function, handling sync or async."""
        result = self.func(*args, **kwargs)
        if inspect.iscoroutine(result):
            # run coroutine
            loop = asyncio.new_event_loop()
            try:
                return loop.run_until_complete(result)
            finally:
                loop.close()
        return result
    def to_dict(self):
        """Serialize metadata for listing or persistence."""
        return {
            'id': self.id,
            'count': self.count,
            'interval': self.interval,
            'last_status': self.last_status,
            'next_run': self.next_run,
        }
    @staticmethod
    def from_dict(data):
        """Reconstruct a Job from persisted data (func is dummy)."""
        job = Job(data.get('id'), lambda: None, interval=data.get('interval'))
        job.count = data.get('count', 0)
        job.last_status = data.get('last_status')
        job.next_run = data.get('next_run')
        return job