import time
from api_validator.performance_metrics import PerformanceMetrics

class Dummy:
    @PerformanceMetrics.report
    def fast(self):
        return 'ok'

def test_report_decorator():
    d = Dummy()
    result = d.fast()
    assert result == 'ok'
    assert hasattr(Dummy.fast, 'last_time')
    assert isinstance(Dummy.fast.last_time, float)
