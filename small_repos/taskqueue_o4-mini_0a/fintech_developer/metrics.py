import threading

class MetricsIntegration:
    def __init__(self):
        self._lock = threading.Lock()
        self.throughput = {}
        self.latency = {}
        self.retry_rate = {}
        self.failure_rate = {}

    def record_throughput(self, payment_type, count=1):
        with self._lock:
            self.throughput[payment_type] = self.throughput.get(payment_type, 0) + count

    def record_latency(self, payment_type, ms):
        with self._lock:
            self.latency.setdefault(payment_type, []).append(ms)

    def record_retry(self, payment_type, count=1):
        with self._lock:
            self.retry_rate[payment_type] = self.retry_rate.get(payment_type, 0) + count

    def record_failure(self, payment_type, count=1):
        with self._lock:
            self.failure_rate[payment_type] = self.failure_rate.get(payment_type, 0) + count

    def get_metrics(self, payment_type):
        with self._lock:
            return {
                "throughput": self.throughput.get(payment_type, 0),
                "latency": list(self.latency.get(payment_type, [])),
                "retry_rate": self.retry_rate.get(payment_type, 0),
                "failure_rate": self.failure_rate.get(payment_type, 0)
            }
