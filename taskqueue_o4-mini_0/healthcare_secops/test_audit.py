import pytest
from pipeline.audit import AuditLogging

def test_audit_logging(tmp_path):
    file = tmp_path / "audit.log"
    al = AuditLogging(str(file))
    al.log('enqueue', 't1', {'foo': 'bar'})
    al.log('retry', 't1')
    logs = al.read_logs()
    assert len(logs) == 2
    assert logs[0]['event'] == 'enqueue'
    assert logs[1]['details'] == {}
    assert file.exists()
