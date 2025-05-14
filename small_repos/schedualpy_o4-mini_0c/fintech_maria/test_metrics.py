import pytest
from scheduler.metrics import MetricsExporter

def test_metrics_counters_and_histograms():
    m = MetricsExporter()
    m.inc_counter('a')
    m.inc_counter('a', 2)
    m.inc_counter('b', 5)
    assert m.get_counters()['a'] == 3
    assert m.get_counters()['b'] == 5
    m.observe_histogram('h1', 0.1)
    m.observe_histogram('h1', 0.2)
    hist = m.get_histograms()['h1']
    assert hist == [0.1, 0.2]
