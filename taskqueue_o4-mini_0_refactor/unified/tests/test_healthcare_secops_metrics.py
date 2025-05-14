from healthcare_secops.pipeline.metrics import MetricsIntegration

def test_metrics_integration():
    mi = MetricsIntegration()
    mi.send('duration', 5.2)
    mi.send('errors', 1)
    m = mi.get_metrics()
    assert m == [{'name': 'duration', 'value': 5.2}, {'name': 'errors', 'value': 1}]
