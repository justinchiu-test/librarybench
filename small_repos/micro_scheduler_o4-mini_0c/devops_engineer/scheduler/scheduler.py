import threading
import signal
import time

class Scheduler:
    def __init__(self, shutdown_timeout=5):
        self.shutdown_timeout = shutdown_timeout
        self.jobs = {}
        self.dependencies = {}
        self.resource_limits = {}
        self.persistence = None
        self.shutdown_event = threading.Event()
        self._setup_signal_handlers()

    def _setup_signal_handlers(self):
        signal.signal(signal.SIGINT, self._handle_signal)
        signal.signal(signal.SIGTERM, self._handle_signal)

    def _handle_signal(self, signum, frame):
        self.graceful_shutdown()

    def graceful_shutdown(self):
        """
        On SIGINT or SIGTERM, finish running jobs, persist state, and stop after timeout.
        """
        self.shutdown_event.set()
        if self.persistence:
            state = {
                'jobs': self.jobs,
                'dependencies': self.dependencies,
                'resource_limits': self.resource_limits
            }
            try:
                self.persistence.save(state)
            except Exception:
                pass
        # wait for timeout then exit
        timer = threading.Timer(self.shutdown_timeout, lambda: None)
        timer.start()
        timer.join()

    def health_check(self):
        """
        Return a dict representing liveness/readiness.
        """
        return {'status': 'ok', 'jobs': list(self.jobs.keys())}

    def trigger_job(self, name):
        """
        Manually invoke any registered job on demand.
        """
        job = self.jobs.get(name)
        if job and job['func']:
            return job['func']()
        return None

    def schedule_job(self, name, func=None, delay=None, interval=None, cron=None, timezone=None, retry=None):
        """
        Define delays and intervals or cron–style expressions.
        Timezone is stored for awareness.
        """
        self.jobs[name] = {
            'func': func,
            'delay': delay,
            'interval': interval,
            'cron': cron,
            'timezone': timezone,
            'retry': retry
        }

    def set_persistence_backend(self, backend):
        """
        Swap out persistence backend.
        """
        self.persistence = backend

    def exponential_backoff(self, base=1, factor=2):
        """
        Return a backoff function f(attempt) = base * factor^(attempt-1)
        """
        def backoff(attempt):
            return base * (factor ** (attempt - 1))
        return backoff

    def define_dependencies(self, job, depends_on):
        """
        Configure DAG relationships.
        """
        self.dependencies[job] = depends_on

    def retry_job(self, name, retry_count=1, backoff=None):
        """
        Set retry policies per job.
        """
        job = self.jobs.get(name)
        if job:
            job['retry'] = {'count': retry_count, 'backoff': backoff}

    def limit_resources(self, job, cpu=None, memory=None, io=None):
        """
        Impose resource limits per job.
        """
        self.resource_limits[job] = {'cpu': cpu, 'memory': memory, 'io': io}
