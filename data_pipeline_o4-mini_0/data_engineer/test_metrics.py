import pytest
from pipeline.metrics import MonitoringMetrics

def test_counters_and_gauges_and_timers():
    m = MonitoringMetrics()
    m.inc_counter('recs')
    m.inc_counter('recs', 2)
    assert m.counters['recs'] == 3
    m.set_gauge('level', 10)
    assert m.gauges['level'] == 10
    with m.time_context('t1'):
        pass
    assert 't1' in m.timers
    assert isinstance(m.timers['t1'][0], float)
