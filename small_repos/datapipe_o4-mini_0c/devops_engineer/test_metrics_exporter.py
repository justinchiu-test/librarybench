import time
import urllib.request
from pipeline.metrics_exporter import MetricsExporter
from pipeline.metrics import Metrics

def test_metrics_exporter_serves_metrics():
    m = Metrics()
    m.increment_counter('s1', 'success')
    exporter = MetricsExporter(m, host='127.0.0.1', port=8001)
    exporter.start()
    time.sleep(0.1)
    resp = urllib.request.urlopen('http://127.0.0.1:8001/metrics')
    text = resp.read().decode()
    assert 'pipeline_s1_success 1' in text
    exporter.stop()
