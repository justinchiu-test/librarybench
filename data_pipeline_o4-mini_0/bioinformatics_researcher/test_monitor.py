from pipeline.monitor import MonitoringMetrics

def test_monitoring_metrics():
    m = MonitoringMetrics()
    m.inc('reads', 5)
    m.inc('reads', 3)
    assert m.get_counters()['reads'] == 8
    m.record_time('sample1', 0.5)
    m.record_time('sample1', 0.7)
    timings = m.get_timings()
    assert 'sample1' in timings and len(timings['sample1']) == 2
    snap = m.snapshot()
    assert 'counters' in snap and 'timings' in snap
