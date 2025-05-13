import queue

class DistributedExecution:
    def __init__(self):
        self._queue = queue.Queue()

    def produce(self, job):
        self._queue.put(job)

    def consume(self, callback):
        try:
            job = self._queue.get_nowait()
        except queue.Empty:
            return None
        try:
            callback(job)
            return job
        except Exception:
            # Requeue for retry on failure
            self._queue.put(job)
            raise
