import pytest
import time
from ml_engineer.orchestrator import Orchestrator, MetricsIntegration, QuotaManagement, CircuitBreaker, AuditLogging

def test_metrics():
    m = MetricsIntegration()
    m.record_batch_duration('team1', 1.2)
    m.record_batch_duration('team1', 2.3)
    assert m.get_batch_durations('team1') == [1.2, 2.3]
    m.record_resource_utilization('team1', 0.5, 100)
    assert m.get_resource_utilization('team1')[0] == {'cpu': 0.5, 'mem': 100}
    m.record_retry('task1')
    m.record_retry('task1')
    assert m.get_retries('task1') == 2
    m.record_failure('task1')
    assert m.get_failures('task1') == 1

def test_quota():
    q = QuotaManagement()
    q.set_quota('team1', 1, 2, 3)
    q.allocate('team1', 1, 1, 1)
    assert q.get_usage('team1') == {'gpus':1, 'cpus':1, 'mem':1}
    with pytest.raises(RuntimeError):
        q.allocate('team1', 1, 0, 0)
    q.release('team1', 1, 1, 1)
    assert q.get_usage('team1') == {'gpus':0, 'cpus':0, 'mem':0}

def test_multi_tenancy_and_audit():
    orch = Orchestrator()
    orch.multi.create_team('team1')
    task_id = orch.multi.submit_task('team1', lambda: None)
    queue = orch.multi.get_queue('team1')
    assert len(queue) == 1 and queue[0][0] == task_id
    orch.multi.store_artifact('team1', 'model', b'data')
    assert orch.multi.get_artifact('team1', 'model') == b'data'
    logs = orch.audit.get_logs('team1')
    assert any(e['event'] == 'submit_task' for e in logs)

def test_task_chaining():
    orch = Orchestrator()
    orch.multi.create_team('team1')
    def t1(): return 1
    def t2(): return 2
    results = orch.chain.run_workflow('team1', [t1, t2])
    assert results == [1, 2]

def test_circuit_breaker():
    cb = CircuitBreaker(threshold=2, reset_timeout=1)
    key = 'api'
    assert not cb.is_open(key)
    cb.record_failure(key)
    assert not cb.is_open(key)
    cb.record_failure(key)
    assert cb.is_open(key)
    time.sleep(1.1)
    assert not cb.is_open(key)

def test_audit_logging():
    a = AuditLogging()
    a.log('team1', {'event':'e'})
    logs = a.get_logs('team1')
    assert logs and logs[0]['event'] == 'e' and 'timestamp' in logs[0]

def test_scheduler_and_delayed():
    orch = Orchestrator()
    orch.multi.create_team('team1')
    ran = []
    def f(): ran.append(True)
    orch.scheduler.schedule('team1', f, delay=0)
    orch.scheduler.run_due()
    assert ran == [True]
    logs = orch.audit.get_logs('team1')
    assert any(e['event'] == 'delayed_task_run' for e in logs)

def test_payload_and_encryption():
    orch = Orchestrator()
    orch.multi.create_team('team1')
    data = b'secret'
    orch.payload.save_payload('team1', 'key1', data)
    loaded = orch.payload.load_payload('team1', 'key1')
    assert loaded == data

def test_cli_launch_status_cancel_logs(capsys):
    orch = Orchestrator()
    orch.multi.create_team('team1')
    orch.cli.run(['launch', '--team', 'team1'])
    orch.cli.run(['status', '--team', 'team1'])
    captured = capsys.readouterr()
    assert 'Launched' in captured.out
    assert 'status' not in captured.out
    tid = orch.multi.submit_task('team1', lambda: None)
    orch.cli.run(['cancel', '--team', 'team1', '--task_id', tid])
    captured = capsys.readouterr()
    assert 'Cancelled' in captured.out
    orch.cli.run(['logs', '--team', 'team1'])
    captured = capsys.readouterr()
    assert 'submit_task' in captured.out
