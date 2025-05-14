import time

class Metrics:
    def __init__(self):
        self.success_count = 0
        self.failure_count = 0
        self.retry_counts = {}
        self.latencies = []

    def record_success(self):
        self.success_count += 1

    def record_failure(self):
        self.failure_count += 1

    def record_retry(self, task_id):
        self.retry_counts[task_id] = self.retry_counts.get(task_id, 0) + 1

    def record_latency(self, duration):
        self.latencies.append(duration)

    def summary(self):
        total = self.success_count + self.failure_count
        success_ratio = self.success_count / total if total else 0
        avg_latency = sum(self.latencies) / len(self.latencies) if self.latencies else 0
        return {
            'success_count': self.success_count,
            'failure_count': self.failure_count,
            'success_ratio': success_ratio,
            'avg_latency': avg_latency,
            'retry_counts': dict(self.retry_counts)
        }
