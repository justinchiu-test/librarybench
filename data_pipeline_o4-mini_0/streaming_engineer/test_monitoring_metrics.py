import time
from monitoring_metrics import MonitoringMetrics

def test_counters_and_gauges_and_timer():
    m = MonitoringMetrics()
    m.inc_counter('a')
    m.inc_counter('a', 2)
    assert m.counters['a'] == 3
    m.set_gauge('g', 5)
    assert m.gauges['g'] == 5
    with m.timer('t'):
        time.sleep(0.01)
    assert 't' in m.timers
    assert m.timers['t'] >= 0
