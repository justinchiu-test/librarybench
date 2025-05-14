from telemetry.metrics import export_prometheus_metrics

def test_export_metrics():
    counters = {'m1': 5, 'm2': 0}
    text = export_prometheus_metrics(counters)
    assert "# TYPE m1 gauge" in text
    assert "m1 5" in text
    assert "# TYPE m2 gauge" in text
    assert "m2 0" in text
