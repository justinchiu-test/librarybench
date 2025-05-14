import threading
import re
from pipeline.metrics import MetricsManager, metrics_manager, increment_counter, export_prometheus_metrics

def test_increment_counter():
    metrics_manager.reset()
    increment_counter('stage1', 'processed')
    increment_counter('stage1', 'processed', 2)
    counters = metrics_manager.get_counters('stage1')
    assert counters['processed'] == 3

def test_thread_safety():
    metrics_manager.reset()
    def worker():
        for _ in range(1000):
            increment_counter('stage1', 'processed')
    threads = [threading.Thread(target=worker) for _ in range(10)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()
    assert metrics_manager.get_counters('stage1')['processed'] == 10000

def test_export_prometheus_metrics():
    metrics_manager.reset()
    increment_counter('s', 'failed', 5)
    text = export_prometheus_metrics()
    assert 'pipeline_failed_total{stage="s"} 5' in text
