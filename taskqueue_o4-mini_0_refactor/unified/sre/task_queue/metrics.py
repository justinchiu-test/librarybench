class MetricsIntegration:
    def __init__(self):
        # queue_depth per tenant
        self.queue_depth = {}
        # list of recorded latencies
        self.worker_latency = []
        # retry_counts per tenant
        self.retry_counts = {}
        # error_rates per tenant
        self.error_rates = {}

    def inc_queue_depth(self, tenant):
        self.queue_depth.setdefault(tenant, 0)
        self.queue_depth[tenant] += 1

    def dec_queue_depth(self, tenant):
        self.queue_depth.setdefault(tenant, 0)
        if self.queue_depth[tenant] > 0:
            self.queue_depth[tenant] -= 1

    def record_latency(self, latency):
        # latency in seconds
        self.worker_latency.append(latency)

    def inc_retry(self, tenant):
        self.retry_counts.setdefault(tenant, 0)
        self.retry_counts[tenant] += 1

    def inc_error(self, tenant):
        self.error_rates.setdefault(tenant, 0)
        self.error_rates[tenant] += 1

    def get_queue_depth(self, tenant):
        return self.queue_depth.get(tenant, 0)

    def get_average_latency(self):
        if not self.worker_latency:
            return 0
        return sum(self.worker_latency) / len(self.worker_latency)

    def get_retry_count(self, tenant):
        return self.retry_counts.get(tenant, 0)

    def get_error_rate(self, tenant):
        return self.error_rates.get(tenant, 0)
