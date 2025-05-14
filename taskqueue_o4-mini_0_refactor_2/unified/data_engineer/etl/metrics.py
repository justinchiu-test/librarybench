import time

class MetricsIntegration:
    def __init__(self):
        self.tasks_started = 0
        self.tasks_succeeded = 0
        self.tasks_failed = 0
        self.latencies = []

    def record_start(self, task_id):
        self.tasks_started += 1

    def record_success(self, task_id, latency):
        self.tasks_succeeded += 1
        try:
            self.latencies.append(float(latency))
        except:
            pass

    def record_failure(self, task_id):
        self.tasks_failed += 1

    def get_metrics(self):
        avg_latency = sum(self.latencies) / len(self.latencies) if self.latencies else 0.0
        return {
            "tasks_started": self.tasks_started,
            "tasks_succeeded": self.tasks_succeeded,
            "tasks_failed": self.tasks_failed,
            "avg_latency": avg_latency
        }
