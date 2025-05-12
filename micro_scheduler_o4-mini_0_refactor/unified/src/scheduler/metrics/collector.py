"""
Collect and render basic scheduler metrics.
"""
import time

class MetricsCollector:
    def __init__(self):
        self.success = {}
        self.failure = {}
        self.latency = {}
    def increment_success(self, job_id):
        self.success[job_id] = self.success.get(job_id, 0) + 1
    def increment_failure(self, job_id):
        self.failure[job_id] = self.failure.get(job_id, 0) + 1
    def record_latency(self, job_id, value):
        lst = self.latency.setdefault(job_id, [])
        lst.append(value)
    def render(self):
        lines = []
        # total run counts
        for jid, cnt in self.success.items():
            lines.append(f'job_runs_total{{job_id="{jid}"}} {cnt}')
        # total failure counts
        for jid, cnt in self.failure.items():
            lines.append(f'job_failures_total{{job_id="{jid}"}} {cnt}')
        # latency histogram count
        for jid, lst in self.latency.items():
            lines.append(f'job_latency_seconds_count{{job_id="{jid}"}} {len(lst)}')
        return '\n'.join(lines)