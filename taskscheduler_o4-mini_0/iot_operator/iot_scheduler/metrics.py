class MetricsExporter:
    def __init__(self):
        self.push_counts = {}
        self.latencies = {}
        self.success_counts = {}
        self.failure_counts = {}

    def inc_push_count(self, device_group):
        self.push_counts[device_group] = self.push_counts.get(device_group, 0) + 1

    def observe_latency(self, device_group, value):
        self.latencies.setdefault(device_group, []).append(value)

    def inc_success(self, device_group):
        self.success_counts[device_group] = self.success_counts.get(device_group, 0) + 1

    def inc_failure(self, device_group):
        self.failure_counts[device_group] = self.failure_counts.get(device_group, 0) + 1

def export_metrics():
    return MetricsExporter()
