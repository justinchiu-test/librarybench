from pipeline.metrics import create_counter
from pipeline.errors import UnrecoverableError

class DataPipeline:
    def __init__(self):
        self.skip_on_error = False
        self.rate_limit = None
        self.streaming = False

        # Create (or reuse) the 'processed' counter, then reset it
        self.counter_processed = create_counter('processed')
        with self.counter_processed._lock:
            self.counter_processed._value = 0

        # Create (or reuse) the 'failed' counter, then reset it
        self.counter_failed = create_counter('failed')
        with self.counter_failed._lock:
            self.counter_failed._value = 0

    def enable_streaming(self):
        self.streaming = True

    def set_skip_on_error(self, skip=True):
        self.skip_on_error = skip

    def set_rate_limit(self, rate):
        self.rate_limit = rate

    def _process(self):
        # placeholder for actual processing logic
        pass

    def run(self):
        try:
            self._process()
            self.counter_processed.inc()
        except Exception as e:
            self.counter_failed.inc()
            if isinstance(e, UnrecoverableError):
                raise
            if not self.skip_on_error:
                raise
        return "running"
