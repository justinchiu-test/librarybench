from threading import Lock

class ConcurrencyLimits:
    _global_count = 0
    _global_lock = Lock()

    def __init__(self, job_name, per_job_limit=1, global_limit=10):
        self.job_name = job_name
        self.per_job_limit = per_job_limit
        self.global_limit = global_limit
        self._job_count = 0
        self._job_lock = Lock()

    def acquire(self):
        with self._job_lock:
            if self._job_count >= self.per_job_limit:
                raise RuntimeError("Per-job concurrency limit exceeded")
            self._job_count += 1
        with ConcurrencyLimits._global_lock:
            if ConcurrencyLimits._global_count >= self.global_limit:
                with self._job_lock:
                    self._job_count -= 1
                raise RuntimeError("Global concurrency limit exceeded")
            ConcurrencyLimits._global_count += 1

    def release(self):
        with self._job_lock:
            if self._job_count > 0:
                self._job_count -= 1
        with ConcurrencyLimits._global_lock:
            if ConcurrencyLimits._global_count > 0:
                ConcurrencyLimits._global_count -= 1
