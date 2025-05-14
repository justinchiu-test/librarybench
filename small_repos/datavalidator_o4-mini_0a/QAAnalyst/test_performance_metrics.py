import time
from datavalidation.performance_metrics import PerformanceMetrics

def test_report_performance_decorator():
    pm = PerformanceMetrics()
    @pm.report_performance
    def dummy(x):
        time.sleep(0.01)
        return x
    result = dummy(5)
    assert result == 5
    assert 'dummy' in pm.metrics
    assert pm.metrics['dummy'] >= 0
