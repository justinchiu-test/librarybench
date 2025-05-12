from pipeline.server import start_prometheus_exporter
from pipeline.counter import create_counter

def test_prometheus_exporter_metrics():
    # create and increment counters
    c1 = create_counter("c1")
    c2 = create_counter("c2")
    c1.inc(2)
    c2.inc(3)
    exporter = start_prometheus_exporter(host="127.0.0.1", port=9000)
    metrics = exporter.get_metrics()
    assert metrics["c1"] == 2
    assert metrics["c2"] == 3
    assert exporter.host == "127.0.0.1"
    assert exporter.port == 9000
