import time
from scheduler.monitoring import MonitoringDashboard

def test_monitoring_stats():
    md = MonitoringDashboard()
    now = time.time()
    md.record_poll("dev1")
    md.record_error("dev1")
    md.update_backlog(42)
    md.update_last_seen("dev2", now - 100)
    stats = md.get_stats()
    assert stats['polls'] == 1
    assert stats['errors'] == 1
    assert stats['backlog'] == 42
    assert 'dev1' in stats['last_seen']
    assert stats['last_seen']['dev2'] == now - 100
