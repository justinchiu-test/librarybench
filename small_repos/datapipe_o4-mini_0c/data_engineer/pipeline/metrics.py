import threading

class MetricsManager:
    def __init__(self):
        self._lock = threading.Lock()
        self._counters = {}

    def reset(self):
        with self._lock:
            self._counters = {}

    def increment_counter(self, stage, counter_name, amount=1):
        with self._lock:
            if stage not in self._counters:
                self._counters[stage] = {'processed': 0, 'succeeded': 0, 'failed': 0}
            if counter_name not in self._counters[stage]:
                self._counters[stage][counter_name] = 0
            self._counters[stage][counter_name] += amount

    def get_counters(self, stage=None):
        with self._lock:
            if stage:
                return dict(self._counters.get(stage, {}))
            else:
                return {st: dict(c) for st, c in self._counters.items()}

    def export_prometheus_metrics(self):
        lines = []
        with self._lock:
            for stage, counters in self._counters.items():
                for name, value in counters.items():
                    metric_name = f"pipeline_{name}_total"
                    lines.append(f'{metric_name}{{stage="{stage}"}} {value}')
        return '\n'.join(lines)

metrics_manager = MetricsManager()

def increment_counter(stage, counter_name, amount=1):
    return metrics_manager.increment_counter(stage, counter_name, amount)

def export_prometheus_metrics():
    return metrics_manager.export_prometheus_metrics()
