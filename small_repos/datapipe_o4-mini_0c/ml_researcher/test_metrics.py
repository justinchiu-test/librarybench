from feature_pipeline.metrics import PrometheusMetrics

def test_metrics_inc_and_observe():
    m = PrometheusMetrics()
    m.inc("cnt", 2)
    m.observe("lat", 0.5)
    families = list(m.registry.collect())
    names = [fam.name for fam in families]
    assert "cnt" in names
    assert "lat" in names
