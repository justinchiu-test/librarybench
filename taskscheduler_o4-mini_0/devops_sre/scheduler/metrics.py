from collections import defaultdict

class Metrics:
    def __init__(self):
        self._success_counts = defaultdict(int)
        self._failure_counts = defaultdict(int)
        self._queue_lengths = {}
        self._latencies = defaultdict(list)

    def increment_success(self, task_name):
        self._success_counts[task_name] += 1

    def increment_failure(self, task_name):
        self._failure_counts[task_name] += 1

    def set_queue_length(self, task_name, length):
        self._queue_lengths[task_name] = length

    def observe_latency(self, task_name, latency):
        self._latencies[task_name].append(latency)

    def success_count(self, task_name):
        return self._success_counts.get(task_name, 0)

    def failure_count(self, task_name):
        return self._failure_counts.get(task_name, 0)

    def queue_length(self, task_name):
        return self._queue_lengths.get(task_name, 0)

    def latencies(self, task_name):
        return list(self._latencies.get(task_name, []))
