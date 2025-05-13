from scheduler.metrics import MetricsExporter
import time

def test_metrics_record_and_export():
    me = MetricsExporter()
    me.record_start('r1')
    time.sleep(0.01)
    me.record_end('r1')
    me.record_failure('r2')
    export = me.export()
    assert 'r1' in export
    assert 'start_time' in export['r1']
    assert 'end_time' in export['r1']
    assert export['r2']['failed'] is True
