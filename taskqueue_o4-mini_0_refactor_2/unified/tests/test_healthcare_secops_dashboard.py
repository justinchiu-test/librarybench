import pytest
from healthcare_secops.pipeline.scheduler import DelayedTaskScheduling
from healthcare_secops.pipeline.dead_letter import DeadLetterQueue
from healthcare_secops.pipeline.metrics import MetricsIntegration
from healthcare_secops.pipeline.audit import AuditLogging
from healthcare_secops.pipeline.dashboard import WebDashboard
from datetime import datetime

def test_dashboard_status(tmp_path):
    sched = DelayedTaskScheduling()
    dt = datetime(2021,1,1,1,0)
    sched.schedule('t1', dt)
    dlq = DeadLetterQueue()
    dlq.enqueue('t2', 'err')
    metrics = MetricsIntegration()
    metrics.send('m1', 1)
    audit_file = tmp_path / "audit.log"
    audit = AuditLogging(str(audit_file))
    audit.log('e1', 't1')
    db = WebDashboard(sched, dlq, metrics, audit)
    status = db.get_status()
    assert 'scheduled_tasks' in status
    assert status['scheduled_tasks']['t1'] == dt
    assert any(item['task_id'] == 't2' for item in status['dead_letters'])
    assert status['metrics'][0]['name'] == 'm1'
    assert status['audit_logs'][0]['event'] == 'e1'
