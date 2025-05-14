import time
class MetricsExporter:
    def __init__(self):
        self.metrics = {}
    def record_start(self, run_id):
        self.metrics.setdefault(run_id, {})['start_time'] = time.time()
    def record_end(self, run_id):
        self.metrics.setdefault(run_id, {})['end_time'] = time.time()
    def record_failure(self, run_id):
        self.metrics.setdefault(run_id, {})['failed'] = True
    def export(self):
        return {rid: dict(vals) for rid, vals in self.metrics.items()}
