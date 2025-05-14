from prometheus_client import Counter, Histogram, Gauge, CollectorRegistry

registry = CollectorRegistry()
job_duration = Histogram(
    'job_duration_seconds',
    'Job duration in seconds',
    ['task_id'],
    registry=registry
)
job_success = Counter(
    'job_success_total',
    'Number of successful jobs',
    ['task_id'],
    registry=registry
)
job_failure = Counter(
    'job_failure_total',
    'Number of failed jobs',
    ['task_id'],
    registry=registry
)
cpu_utilization = Gauge('cpu_utilization', 'CPU utilization percent', registry=registry)
gpu_utilization = Gauge('gpu_utilization', 'GPU utilization percent', registry=registry)

def observe_duration(task_id, duration):
    job_duration.labels(task_id=task_id).observe(duration)

def increment_success(task_id):
    job_success.labels(task_id=task_id).inc()

def increment_failure(task_id):
    job_failure.labels(task_id=task_id).inc()

def set_cpu_util(val):
    cpu_utilization.set(val)

def set_gpu_util(val):
    gpu_utilization.set(val)
