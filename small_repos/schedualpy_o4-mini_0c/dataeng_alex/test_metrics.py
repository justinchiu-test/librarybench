import time
from datetime import datetime, timedelta
from scheduler import ThreadSafeScheduler

def test_metrics_counts_and_drift():
    scheduler = ThreadSafeScheduler()
    scheduler.schedule('m1', lambda: None, cron_expr=1)
    scheduler.schedule_one_off('m2', lambda: None, run_at=datetime.now()+timedelta(seconds=1))
    time.sleep(1.1)
    scheduler._run_pending()
    time.sleep(0.1)
    metrics = scheduler.emit_metrics()
    assert metrics['success_counts']['m1'] == 1
    assert metrics['success_counts']['m2'] == 1
    assert 'm1' in metrics['job_durations']
    assert 'm2' in metrics['schedule_lag']
