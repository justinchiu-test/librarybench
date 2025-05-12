from metrics import export_prometheus_metrics, get_metric

def test_metrics_export_and_get():
    export_prometheus_metrics('latency', 123)
    export_prometheus_metrics('throughput', 456)
    assert get_metric('latency') == 123
    assert get_metric('throughput') == 456
    assert get_metric('unknown') is None
