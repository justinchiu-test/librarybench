from data_scientist.ml_pipeline.metrics import registry, job_duration, job_success, job_failure, observe_duration, increment_success, increment_failure, set_cpu_util, set_gpu_util

def test_metrics_observation():
    observe_duration("t1", 0.5)
    increment_success("t1")
    increment_failure("t1")
    set_cpu_util(75.0)
    set_gpu_util(33.3)
    metrics = registry.collect()
    names = {m.name for m in metrics}
    assert 'job_duration_seconds' in names
    # Adjusted to match metric names without suffix
    assert 'job_success' in names
    assert 'job_failure' in names
    assert 'cpu_utilization' in names
    assert 'gpu_utilization' in names
