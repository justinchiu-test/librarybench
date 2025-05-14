import time
from performance_metrics import PerformanceMetrics

def test_performance_metrics():
    pm = PerformanceMetrics()
    pm.start()
    pm.increment(5)
    time.sleep(0.1)
    rep = pm.report()
    assert rep['count'] == 5
    assert rep['elapsed'] > 0
    assert rep['throughput'] == pytest.approx(5/rep['elapsed'], rel=1e-2)
